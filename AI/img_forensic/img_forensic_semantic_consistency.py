"""
semantic_consistency.py (patched, Option-A)
Forensic-grade semantic & physical consistency analysis with robust fallbacks.
"""

import os
import math
import traceback
import numpy as np
import cv2
import torch
import mediapipe as mp
import warnings
import logging
from PIL import Image
from typing import Dict, Tuple

os.environ["YOLO_VERBOSE"] = "False"
os.environ["ULTRALYTICS_VERBOSITY"] = "0"
warnings.filterwarnings("ignore")
logging.getLogger("torch.hub").setLevel(logging.NOTSET)

device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    import open_clip
    OPENCLIP_AVAILABLE = True
except Exception:
    OPENCLIP_AVAILABLE = False

try:
    MEDIAPIPE_AVAILABLE = True
except Exception:
    MEDIAPIPE_AVAILABLE = False

try:
    from ultralytics import YOLO

    ULTRALYTICS_AVAILABLE = True
except Exception:
    ULTRALYTICS_AVAILABLE = False

try:
    from transformers import ViTImageProcessor, ViTForImageClassification

    VIT_AVAILABLE = True
except Exception:
    VIT_AVAILABLE = False

if not OPENCLIP_AVAILABLE:
    try:
        from transformers import CLIPProcessor, CLIPModel

        HF_CLIP_AVAILABLE = True
    except Exception:
        HF_CLIP_AVAILABLE = False
else:
    HF_CLIP_AVAILABLE = False

try:
    midas = torch.hub.load("intel-isl/MiDaS", "DPT_Large").to(device)
    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms").dpt_transform
    MIDAS_AVAILABLE = True
except Exception:
    MIDAS_AVAILABLE = False

OPENCLIP_LOADED = False
clip_model = None
clip_preprocess = None
open_clip_tokenize = None

if OPENCLIP_AVAILABLE:
    candidate_tags = [
        "laion2b_s32b_b82k",
        "laion400m_e31",
        "laion400m_e32",
        "openai",
        "laion2b_s32b_b79k",
    ]
    for tag in candidate_tags:
        try:
            model_tmp, _, preprocess_tmp = open_clip.create_model_and_transforms(
                "ViT-L-14", pretrained=tag
            )
            clip_model = model_tmp.to(device)
            clip_preprocess = preprocess_tmp
            open_clip_tokenize = open_clip.tokenize
            OPENCLIP_LOADED = True
            break
        except Exception:
            continue

HF_CLIP_LOADED = False
if not OPENCLIP_LOADED and HF_CLIP_AVAILABLE:
    try:
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").to(
            device
        )
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        HF_CLIP_LOADED = True
    except Exception:
        HF_CLIP_LOADED = False

VIT_LOADED = False
if VIT_AVAILABLE:
    try:
        vit_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
        vit_model = ViTForImageClassification.from_pretrained(
            "google/vit-base-patch16-224"
        ).to(device)
        VIT_LOADED = True
    except Exception:
        VIT_LOADED = False

YOLO_LOADED = False
yolo = None
if ULTRALYTICS_AVAILABLE:
    try:
        try:
            yolo = YOLO("yolov8n-seg.pt")
        except Exception:
            yolo = YOLO("yolov8n.pt")
        YOLO_LOADED = True
    except Exception:
        YOLO_LOADED = False


def safe_score(x: float) -> float:
    try:
        if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))):
            return 0.0
        return float(max(0.0, min(1.0, float(x))))
    except Exception:
        return 0.0


def pil_to_rgb_np(pil_img: Image.Image) -> np.ndarray:
    return np.array(pil_img.convert("RGB"))


def estimate_anatomy_validity(pil_img: Image.Image) -> float:
    try:
        img = pil_to_rgb_np(pil_img)
        H, W = img.shape[:2]
        if MEDIAPIPE_AVAILABLE:
            mp_pose = mp.solutions.pose
            with mp_pose.Pose(static_image_mode=True) as pose:
                res = pose.process(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                if not res.pose_landmarks:
                    return 0.0
                lm = res.pose_landmarks.landmark
                keypoints = np.array([[l.x * W, l.y * H, l.visibility] for l in lm])
        else:
            return 0.5

        def get(idx):
            if idx < keypoints.shape[0]:
                return keypoints[idx, :2], keypoints[idx, 2]
            return None, 0.0

        idx_map = {
            "l_sh": 11,
            "r_sh": 12,
            "l_el": 13,
            "r_el": 14,
            "l_wr": 15,
            "r_wr": 16,
            "l_hip": 23,
            "r_hip": 24,
            "l_knee": 25,
            "r_knee": 26,
            "l_ank": 27,
            "r_ank": 28,
        }
        pts = {}
        confs = {}
        for k, i in idx_map.items():
            p, c = get(i)
            pts[k] = p
            confs[k] = c

        valid_kp = sum(1 for v in confs.values() if v > 0.2)
        if valid_kp < 4:
            return 0.5

        def dist(a, b):
            return np.linalg.norm(a - b) if a is not None and b is not None else np.nan

        left_arm = dist(pts["l_sh"], pts["l_el"]) + dist(pts["l_el"], pts["l_wr"])
        right_arm = dist(pts["r_sh"], pts["r_el"]) + dist(pts["r_el"], pts["r_wr"])
        left_leg = dist(pts["l_hip"], pts["l_knee"]) + dist(pts["l_knee"], pts["l_ank"])
        right_leg = dist(pts["r_hip"], pts["r_knee"]) + dist(
            pts["r_knee"], pts["r_ank"]
        )
        torso = dist(pts["l_sh"], pts["r_sh"]) + dist(pts["l_hip"], pts["r_hip"])

        lengths = [left_arm, right_arm, left_leg, right_leg, torso]
        lengths = [l for l in lengths if not np.isnan(l) and l > 1e-6]
        if len(lengths) < 3:
            return 0.6

        sym_arm = 1 - abs(left_arm - right_arm) / max(left_arm, right_arm, 1e-6)
        sym_leg = 1 - abs(left_leg - right_leg) / max(left_leg, right_leg, 1e-6)
        sym_score = np.mean(
            [
                sym_arm if not np.isnan(sym_arm) else 0.5,
                sym_leg if not np.isnan(sym_leg) else 0.5,
            ]
        )

        limb_ratios = []
        for L in [left_arm, right_arm, left_leg, right_leg]:
            if not np.isnan(L):
                limb_ratios.append(L / max(torso, 1e-6))
        limb_ratios = np.array(limb_ratios)
        plausible = np.logical_and(limb_ratios > 0.4, limb_ratios < 2.5)
        prop_score = float(np.sum(plausible) / max(len(limb_ratios), 1))

        final = 0.6 * sym_score + 0.4 * prop_score
        return safe_score(final)

    except Exception:
        traceback.print_exc()
        return 0.0


def estimate_physics_correctness(pil_img: Image.Image) -> float:
    try:
        img = pil_to_rgb_np(pil_img)
        H, W = img.shape[:2]
        instances = []

        if YOLO_LOADED:
            results = yolo(img, imgsz=640)[0]
            for b in results.boxes:
                xyxy = b.xyxy[0].cpu().numpy()
                conf = float(b.conf.cpu().numpy())
                cls = int(b.cls.cpu().numpy())
                instances.append({"box": np.array(xyxy), "score": conf, "class": cls})
        else:
            return 0.6

        n = len(instances)
        if n == 0:
            return 0.6

        support_counts = np.zeros(n, dtype=int)
        float_flags = np.zeros(n, dtype=bool)

        for i in range(n):
            x1, y1, x2, y2 = instances[i]["box"]
            bottom_y = y2
            for j in range(n):
                if i == j:
                    continue
                xx1, yy1, xx2, yy2 = instances[j]["box"]
                if yy1 < bottom_y and yy1 > (bottom_y - max(10, H * 0.02)):
                    overlap_w = max(0, min(x2, xx2) - max(x1, xx1))
                    frac = overlap_w / max((x2 - x1), 1e-6)
                    if frac > 0.3:
                        support_counts[i] += 1
            if support_counts[i] == 0 and (bottom_y < 0.98 * H):
                float_flags[i] = True

        non_float_ratio = 1.0 - float(np.sum(float_flags) / n)
        avg_conf = np.mean([inst["score"] for inst in instances]) if instances else 0.5
        score = 0.7 * non_float_ratio + 0.3 * avg_conf
        return safe_score(score)

    except Exception:
        traceback.print_exc()
        return 0.0


def estimate_depth_and_perspective(pil_img: Image.Image) -> Tuple[float, np.ndarray]:
    try:
        img = pil_to_rgb_np(pil_img)
        h, w = img.shape[:2]
        depth_map = None

        if MIDAS_AVAILABLE:
            input_data = midas_transforms(img)
            if isinstance(input_data, dict):
                tensor = input_data.get("image")
            else:
                tensor = input_data
            if tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)
            tensor = tensor.to(device)
            with torch.no_grad():
                prediction = midas(tensor)
            depth_map = prediction.squeeze().cpu().numpy()
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
            depth_map = cv2.GaussianBlur(gray, (21, 21), 0).astype(np.float32)
            if depth_map.max() > 0:
                depth_map = (depth_map - depth_map.min()) / (
                    depth_map.max() - depth_map.min() + 1e-9
                )

        dmin, dmax = float(np.nanmin(depth_map)), float(np.nanmax(depth_map))
        if np.isfinite(dmin) and (dmax - dmin) > 1e-6:
            depth_map = (depth_map - dmin) / (dmax - dmin)
        else:
            depth_map = np.zeros_like(depth_map, dtype=np.float32)

        var = float(np.nanvar(depth_map))
        var_score = 1.0 - (var / (var + 0.5))

        H2, W2 = depth_map.shape[:2]
        sample_n = min(2000, H2 * W2)
        ys = np.random.randint(0, H2, size=sample_n)
        xs = np.random.randint(0, W2, size=sample_n)
        zs = depth_map[ys, xs]
        A = np.stack([xs, ys, np.ones_like(xs)], axis=1)
        try:
            params, *_ = np.linalg.lstsq(A, zs, rcond=None)
            pred = A.dot(params)
            res = np.abs(pred - zs)
            inlier_frac = float(np.mean(res < (0.05 + 0.02 * np.std(zs))))
            plane_score = safe_score(inlier_frac)
        except Exception:
            plane_score = 0.5

        edges = cv2.Canny(
            (cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)).astype(np.uint8), 50, 150
        )
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=80, minLineLength=40, maxLineGap=10
        )
        if lines is None:
            perspective_score = 0.6
        else:
            dirs = []
            for l in lines:
                x1, y1, x2, y2 = l[0]
                ang = math.atan2((y2 - y1), (x2 - x1))
                dirs.append(ang)
            if len(dirs) < 5:
                perspective_score = 0.6
            else:
                hist, _ = np.histogram(dirs, bins=16)
                dominant_frac = float(np.max(hist)) / max(1, len(dirs))
                perspective_score = safe_score(0.5 + 0.5 * dominant_frac)

        score = 0.25 * var_score + 0.45 * plane_score + 0.30 * perspective_score
        return safe_score(score), depth_map

    except Exception:
        traceback.print_exc()
        return 0.0, np.zeros((64, 64), dtype=np.float32)


def estimate_lighting_consistency(
    pil_img: Image.Image, depth_map: np.ndarray = None
) -> float:
    try:
        img = pil_to_rgb_np(pil_img)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
        mag = np.sqrt(gx * gx + gy * gy)
        ang = np.arctan2(gy, gx)
        bins = 36
        hist, edges = np.histogram(ang.flatten(), bins=bins, weights=mag.flatten())
        dominant_angle_centers = (edges[:-1] + edges[1:]) / 2.0
        dom_idx = int(np.argmax(hist)) if hist.size > 0 else 0
        dom_dir = (
            float(dominant_angle_centers[dom_idx])
            if dominant_angle_centers.size > 0
            else 0.0
        )

        normal_consistency = 0.5
        if depth_map is not None and depth_map.size > 10:
            dzdx = cv2.Sobel(depth_map.astype(np.float32), cv2.CV_32F, 1, 0)
            dzdy = cv2.Sobel(depth_map.astype(np.float32), cv2.CV_32F, 0, 1)
            nx = -dzdx
            ny = -dzdy
            nz = np.ones_like(nx) * (np.mean(np.abs(depth_map)) + 1e-6)
            norms = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
            vx = float(np.nanmean((nx / norms)))
            vy = float(np.nanmean((ny / norms)))
            norm_angle = math.atan2(vy, vx)
            ang_diff = min(
                abs(norm_angle - dom_dir), 2 * math.pi - abs(norm_angle - dom_dir)
            )
            normal_consistency = 1.0 - (ang_diff / math.pi)
            normal_consistency = safe_score(normal_consistency)

        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        _, th = cv2.threshold(
            (blurred * 255).astype(np.uint8), int(0.6 * 255), 255, cv2.THRESH_BINARY_INV
        )
        comps = cv2.connectedComponentsWithStats(th, connectivity=8)
        orientations = []
        for lbl in range(1, comps[0]):
            mask = (comps[1] == lbl).astype(np.uint8)
            area = comps[2][lbl, cv2.CC_STAT_AREA]
            if area < 100:
                continue
            ys, xs = np.nonzero(mask)
            if xs.size < 3:
                continue
            cov = np.cov(xs, ys)
            if cov.shape == (2, 2) and np.linalg.cond(cov) < 1e6:
                evals, evecs = np.linalg.eig(cov)
                principal = evecs[:, np.argmax(evals)]
                shadow_angle = math.atan2(principal[1], principal[0])
                orientations.append(shadow_angle)
        if len(orientations) > 0:
            diffs = [
                min(abs(o - dom_dir), 2 * math.pi - abs(o - dom_dir))
                for o in orientations
            ]
            shadow_align = 1.0 - (np.mean(diffs) / math.pi)
            shadow_align = safe_score(shadow_align)
        else:
            shadow_align = 0.6

        hist_strength = float(hist[dom_idx]) if hist.size > 0 else 0.0
        score = (
            0.35 * (1.0 if hist_strength > (0.01 * mag.sum() + 1e-6) else 0.5)
            + 0.45 * normal_consistency
            + 0.20 * shadow_align
        )
        return safe_score(score)

    except Exception:
        traceback.print_exc()
        return 0.0


def estimate_reflection_correctness(
    pil_img: Image.Image, depth_map: np.ndarray = None
) -> float:
    try:
        img = pil_to_rgb_np(pil_img).astype(np.float32) / 255.0
        gray = (
            cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(
                np.float32
            )
            / 255.0
        )

        lap = cv2.Laplacian(gray, cv2.CV_32F)
        local_var = cv2.blur(lap * lap, (15, 15))
        bright = (gray > 0.8).astype(np.uint8)
        reflective_mask = ((local_var > 0.0005) & (bright == 1)).astype(np.uint8)

        reflective_area = float(reflective_mask.sum()) / max(1, gray.size)
        if reflective_area < 0.001:
            return 0.9

        if depth_map is None:
            return safe_score(0.6 + 0.4 * reflective_area)

        dzdx = cv2.Sobel(depth_map.astype(np.float32), cv2.CV_32F, 1, 0)
        dzdy = cv2.Sobel(depth_map.astype(np.float32), cv2.CV_32F, 0, 1)
        nx = -dzdx
        ny = -dzdy
        nz = np.ones_like(nx)
        norms = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        nx = nx / norms
        ny = ny / norms
        nz = nz / norms

        h_n, w_n = nx.shape[:2]
        reflective_mask_rs = cv2.resize(
            reflective_mask.astype(np.uint8),
            (w_n, h_n),
            interpolation=cv2.INTER_NEAREST,
        )

        if reflective_mask_rs.sum() < 10:
            return 0.6

        avg_nx = float(np.mean(nx[reflective_mask_rs == 1]))
        avg_ny = float(np.mean(ny[reflective_mask_rs == 1]))
        avg_nz = float(np.mean(nz[reflective_mask_rs == 1]))

        spec_compat = avg_nz + 0.1 * (avg_nx + avg_ny)
        spec_compat = (spec_compat + 1.0) / 2.0
        light_score = 0.7
        final = 0.4 * light_score + 0.6 * safe_score(spec_compat)
        return safe_score(final)

    except Exception:
        traceback.print_exc()
        return 0.0


def estimate_material_realism(pil_img: Image.Image) -> float:
    try:
        prompts = [
            "a photograph of a real cloth, detailed texture and grain",
            "a photograph of a real metal surface with realistic reflections",
            "a photo of real skin with pores and natural texture",
            "a realistic photograph with natural textures and no generative artifacts",
        ]
        if OPENCLIP_LOADED:
            img_pre = (
                clip_preprocess(Image.fromarray(pil_to_rgb_np(pil_img)))
                .unsqueeze(0)
                .to(device)
            )
            tokens = open_clip_tokenize(prompts).to(device)
            with torch.no_grad():
                img_emb = clip_model.encode_image(img_pre)
                txt_emb = clip_model.encode_text(tokens)
                sims = (img_emb @ txt_emb.T).cpu().numpy().squeeze()
                sims = (sims - sims.min()) / (np.ptp(sims) + 1e-9)
                return safe_score(float(np.mean(sims)))
        elif HF_CLIP_LOADED:
            inputs = clip_processor(
                text=prompts, images=pil_img, return_tensors="pt", padding=True
            ).to(device)
            with torch.no_grad():
                out = clip_model(**inputs)
                sims = out.logits_per_image.softmax(dim=1).cpu().numpy()[0]
                sims = (sims - sims.min()) / (np.ptp(sims) + 1e-9)
                return safe_score(float(np.mean(sims)))
        else:
            return 0.6
    except Exception:
        traceback.print_exc()
        return 0.0


def estimate_object_logic(pil_img: Image.Image) -> float:
    try:
        img = pil_to_rgb_np(pil_img)
        if YOLO_LOADED:
            results = yolo(img, imgsz=640)[0]
            confidences = (
                [float(b.conf.cpu().numpy()) for b in results.boxes]
                if hasattr(results, "boxes")
                else []
            )
            return safe_score(float(np.mean(confidences)) if confidences else 0.5)
        elif VIT_LOADED:
            inputs = vit_processor(images=pil_img, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = vit_model(**inputs)
                probs = outputs.logits.softmax(dim=1)
                confidence = float(probs.max().item())
            return safe_score(confidence)
        elif OPENCLIP_LOADED or HF_CLIP_LOADED:
            prompts = [
                "a realistic photograph of a natural scene",
                "a real photo with consistent objects interacting",
            ]
            if OPENCLIP_LOADED:
                img_pre = (
                    clip_preprocess(Image.fromarray(pil_to_rgb_np(pil_img)))
                    .unsqueeze(0)
                    .to(device)
                )
                tokens = open_clip_tokenize(prompts).to(device)
                with torch.no_grad():
                    img_emb = clip_model.encode_image(img_pre)
                    txt_emb = clip_model.encode_text(tokens)
                    sims = (img_emb @ txt_emb.T).cpu().numpy().squeeze()
                    sims = (sims - sims.min()) / (np.ptp(sims) + 1e-9)
                    return safe_score(float(np.mean(sims)))
            else:
                inputs = clip_processor(
                    text=prompts, images=pil_img, return_tensors="pt", padding=True
                ).to(device)
                with torch.no_grad():
                    out = clip_model(**inputs)
                    sims = out.logits_per_image.softmax(dim=1).cpu().numpy()[0]
                    sims = (sims - sims.min()) / (np.ptp(sims) + 1e-9)
                    return safe_score(float(np.mean(sims)))
        else:
            return 0.5
    except Exception:
        traceback.print_exc()
        return 0.0


def semantic_consistency_analyze(image_path) -> Dict:
    try:
        img_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)

        depth_score, depth_map = estimate_depth_and_perspective(pil_img)

        anatomy = estimate_anatomy_validity(pil_img)
        physics = estimate_physics_correctness(pil_img)
        lighting = estimate_lighting_consistency(pil_img, depth_map)
        reflection = estimate_reflection_correctness(pil_img, depth_map)
        material = estimate_material_realism(pil_img)
        logic = estimate_object_logic(pil_img)

        weights = {
            "anatomy_validity": 0.12,
            "physics_correctness": 0.18,
            "lighting_consistency": 0.20,
            "reflection_correctness": 0.10,
            "depth_and_perspective": 0.20,
            "material_realism": 0.10,
            "object_logic": 0.10,
        }
        vals = {
            "anatomy_validity": anatomy,
            "physics_correctness": physics,
            "lighting_consistency": lighting,
            "reflection_correctness": reflection,
            "depth_and_perspective": depth_score,
            "material_realism": material,
            "object_logic": logic,
        }
        overall = sum(vals[k] * weights[k] for k in vals)

        return {
            "semantic_consistency": {
                "status": "ok",
                "consistency_score": float(safe_score(overall)),
                "details": {k: float(safe_score(vals[k])) for k in vals},
                "notes": "",
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "semantic_consistency": {
                "status": "error",
                "consistency_score": 0.0,
                "details": {
                    "anatomy_validity": 0.0,
                    "physics_correctness": 0.0,
                    "lighting_consistency": 0.0,
                    "reflection_correctness": 0.0,
                    "depth_and_perspective": 0.0,
                    "material_realism": 0.0,
                    "object_logic": 0.0,
                },
                "notes": str(e),
            }
        }
