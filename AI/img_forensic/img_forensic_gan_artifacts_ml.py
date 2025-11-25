import cv2
import torch
import base64
import numpy as np
from pathlib import Path
from typing import Any, Dict, Optional
from PIL import Image, ImageFile

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
CKPT_DIR = MODELS_DIR / "checkpoints"
CKPT_DIR.mkdir(parents=True, exist_ok=True)
WEIGHTS = {
    "fatformer": CKPT_DIR / "fatformer_ckpt.pth",
    "mantranet": CKPT_DIR / "mantranet_ckpt.pth",
    "noiseprint": CKPT_DIR / "noiseprint_ckpt.pth",
    "realesrgan_x4": CKPT_DIR / "RealESRGAN_x4plus.pth"
}

def _to_b64(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")

def _normalize_to_uint8(arr: np.ndarray) -> np.ndarray:
    mn = float(np.min(arr))
    mx = float(np.max(arr))
    if mx - mn < 1e-8:
        return np.clip(arr, 0, 255).astype(np.uint8)
    scaled = 255.0 * (arr - mn) / (mx - mn)
    return np.clip(scaled, 0, 255).astype(np.uint8)

def safe_imread(p: Path):
    img = cv2.imread(str(p), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"cannot read image:{p}")
    return img

def is_jpeg(path: Path):
    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        with Image.open(path) as im:
            return im.format == "JPEG"
    except Exception:
        return False

def estimate_jpeg_compression_artifact_strength(path: Path):
    try:
        with Image.open(path) as im:
            if im.format != "JPEG":
                return 0.0
            info = im.info
            q = info.get("quality", None)
            if q is not None:
                return float(np.clip((95 - q) / 50.0, 0.0, 1.0))
    except Exception:
        pass
    try:
        arr = np.fromfile(str(path), dtype=np.uint8)
        if arr.size < 100:
            return 0.0
        s = np.mean(arr)
        return 0.0
    except Exception:
        return 0.0

def variance_of_laplacian(gray):
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

def detect_portrait_like(gray, img):
    h, w = gray.shape
    face = False
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30,30))
        if len(faces) > 0:
            face = True
    except Exception:
        face = False
    aspect = h / max(1, w)
    centered = False
    if face:
        centered = True
    if aspect > 1.0 and centered:
        return True
    return False

def detect_architecture_pattern(gray):
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=120, minLineLength=min(gray.shape)//6, maxLineGap=20)
    if lines is None:
        return 0.0
    vertical = 0
    horizontal = 0
    for l in lines:
        x1,y1,x2,y2 = l[0]
        if abs(x1-x2) < 6:
            vertical += 1
        if abs(y1-y2) < 6:
            horizontal += 1
    total = vertical + horizontal + 1
    return float(np.clip(max(vertical, horizontal) / total, 0.0, 1.0))

def improved_texture_repetition_score(gray, n_patches=16, patch_size=64):
    h, w = gray.shape
    ps = min(patch_size, max(8, h//6), max(8, w//6))
    rng = np.random.default_rng(123456)
    coords = []
    for _ in range(n_patches):
        y = int(rng.integers(0, max(1, h - ps + 1)))
        x = int(rng.integers(0, max(1, w - ps + 1)))
        coords.append((y, x))
    patches = []
    for (y, x) in coords:
        p = gray[y:y+ps, x:x+ps].astype(np.float32)
        if p.size == 0:
            p = cv2.resize(gray, (ps, ps)).astype(np.float32)
        patches.append((p - p.mean()) / (p.std() + 1e-12))
    scores = []
    for i, pi in enumerate(patches):
        maxcorr = 0.0
        a = _normalize_to_uint8(pi * 30.0 + 128.0)
        for j, pj in enumerate(patches):
            if i == j:
                continue
            b = _normalize_to_uint8(pj * 30.0 + 128.0)
            try:
                res = cv2.matchTemplate(a, b, cv2.TM_CCORR_NORMED)
                val = float(np.max(res))
            except Exception:
                val = 0.0
            if val > maxcorr:
                maxcorr = val
        scores.append(maxcorr)
    if not scores:
        return 0.0
    mean_score = float(np.clip(float(np.mean(scores)), 0.0, 1.0))
    return mean_score

def improved_sampling_artifacts_score(gray):
    g = gray.astype(np.float32)
    h, w = g.shape
    win_y = np.hanning(h)[:, None]
    win_x = np.hanning(w)[None, :]
    gw = g * (win_y * win_x)
    F = np.fft.fftshift(np.fft.fft2(gw))
    mag = np.abs(F)
    total = mag.sum() + 1e-12
    cy, cx = h // 2, w // 2
    yy, xx = np.ogrid[:h, :w]
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    low_r = max(1.0, min(h, w) * 0.06)
    mid_r = max(low_r + 1.0, min(h, w) * 0.22)
    mid_mask = (r >= low_r) & (r < mid_r)
    high_mask = (r >= mid_r)
    band_energy = (mag * mid_mask).sum() + 0.6 * (mag * high_mask).sum()
    ratio = float(band_energy / total)
    val = ratio * 2.2
    return float(np.clip(val, 0.0, 1.0))

def improved_upscale_traces_score(gray):
    h, w = gray.shape
    if h < 32 or w < 32:
        return 0.0
    down = cv2.resize(gray, (max(8, w//2), max(8, h//2)), interpolation=cv2.INTER_AREA)
    up = cv2.resize(down, (w, h), interpolation=cv2.INTER_CUBIC)
    lap_o = cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F)
    lap_u = cv2.Laplacian(up.astype(np.float32), cv2.CV_32F)
    diff = np.abs(lap_o - lap_u)
    flat = diff.flatten()
    if flat.size > 40:
        trimmed = np.sort(flat)[int(len(flat)*0.05): int(len(flat)*0.95)]
    else:
        trimmed = flat
    m = float(np.mean(trimmed)) if trimmed.size else float(np.mean(flat))
    val = m / (m + 8.0)
    return float(np.clip(val, 0.0, 1.0))

def improved_pattern_periodicity_score(gray):
    g = gray.astype(np.float32)
    h, w = g.shape
    F = np.fft.fftshift(np.fft.fft2(g - g.mean()))
    mag = np.abs(F)
    cy, cx = h//2, w//2
    yy, xx = np.indices((h, w))
    r = np.sqrt((yy - cy)**2 + (xx - cx)**2)
    r_max = int(min(h, w) // 2)
    radial = []
    for ri in range(1, r_max):
        mask = (r >= ri) & (r < ri + 1)
        if np.any(mask):
            radial.append(mag[mask].mean())
        else:
            radial.append(0.0)
    radial = np.array(radial, dtype=np.float32)
    if radial.size == 0:
        return 0.0
    radial = (radial - radial.mean()) / (radial.std() + 1e-12)
    periodicity = float(np.std(radial))
    val = periodicity / (periodicity + 3.0)
    return float(np.clip(val, 0.0, 1.0))

def safe_heatmap_and_b64(arr, out_path: Path):
    norm = _normalize_to_uint8(arr)
    cmap = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), cmap)
    return _to_b64(out_path)

class MLWrapper:
    def __init__(self):
        self.fat = None
        self.man = None
        self.noise = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if WEIGHTS["fatformer"].exists():
            try:
                ck = torch.load(str(WEIGHTS["fatformer"]), map_location=self.device)
                self.fat = ck
            except Exception:
                self.fat = None
        if WEIGHTS["mantranet"].exists():
            try:
                ck = torch.load(str(WEIGHTS["mantranet"]), map_location=self.device)
                self.man = ck
            except Exception:
                self.man = None
        if WEIGHTS["noiseprint"].exists():
            try:
                ck = torch.load(str(WEIGHTS["noiseprint"]), map_location=self.device)
                self.noise = ck
            except Exception:
                self.noise = None

    def fatformer_score(self, img: np.ndarray) -> Optional[float]:
        if self.fat is None:
            return None
        try:
            x = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            x = cv2.resize(x, (256, 256), interpolation=cv2.INTER_AREA)
            x = x.astype(np.float32) / 255.0
            t = torch.from_numpy(x).permute(2,0,1).unsqueeze(0).to(self.device)
            with torch.no_grad():
                out = None
                try:
                    model = self.fat.get("model", None)
                    if model is not None and hasattr(model, "eval"):
                        model.to(self.device)
                        model.eval()
                        out = model(t)
                except Exception:
                    out = None
                if out is None:
                    if isinstance(self.fat, dict) and "score" in self.fat:
                        s = float(self.fat["score"])
                        return float(np.clip(s, 0.0, 1.0))
                    return None
                if isinstance(out, torch.Tensor):
                    s = float(out.sigmoid().mean().cpu().numpy())
                    return float(np.clip(s, 0.0, 1.0))
            return None
        except Exception:
            return None

    def mantranet_heat_and_score(self, img: np.ndarray):
        if self.man is None:
            return None, None
        try:
            x = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            x = cv2.resize(x, (256, 256), interpolation=cv2.INTER_AREA)
            t = torch.from_numpy(x.astype(np.float32)/255.0).unsqueeze(0).unsqueeze(0).to(self.device)
            with torch.no_grad():
                out = None
                try:
                    model = self.man.get("model", None)
                    if model is not None and hasattr(model, "eval"):
                        model.to(self.device)
                        model.eval()
                        out = model(t)
                except Exception:
                    out = None
                if out is None:
                    if isinstance(self.man, dict) and "heat" in self.man:
                        h = np.array(self.man["heat"])
                        heat_b64 = safe_heatmap_and_b64(h, CKPT_DIR / "mantranet_heat.jpg")
                        s = float(min(1.0, np.mean(h)))
                        return heat_b64, float(np.clip(s, 0.0, 1.0))
                    return None, None
                if isinstance(out, torch.Tensor):
                    heat = out.squeeze().cpu().numpy()
                    heat_b64 = safe_heatmap_and_b64(heat, CKPT_DIR / "mantranet_heat.jpg")
                    s = float(np.clip(float(np.mean(heat)), 0.0, 1.0))
                    return heat_b64, s
            return None, None
        except Exception:
            return None, None

    def noiseprint_score(self, img: np.ndarray):
        if self.noise is None:
            return None
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            small = cv2.resize(gray, (256, 256), interpolation=cv2.INTER_AREA).astype(np.float32)
            t = torch.from_numpy(small).unsqueeze(0).unsqueeze(0).to(self.device)
            with torch.no_grad():
                out = None
                try:
                    model = self.noise.get("model", None)
                    if model is not None and hasattr(model, "eval"):
                        model.to(self.device)
                        model.eval()
                        out = model(t)
                except Exception:
                    out = None
                if out is None:
                    if isinstance(self.noise, dict) and "score" in self.noise:
                        return float(np.clip(float(self.noise["score"]), 0.0, 1.0))
                    return None
                if isinstance(out, torch.Tensor):
                    residual = out.squeeze().cpu().numpy()
                    score = float(np.clip(np.std(residual) / (np.std(residual) + 1.0), 0.0, 1.0))
                    return score
            return None
        except Exception:
            return None

def gan_artifacts_ml_analyze(image_path: str) -> Dict[str, Any]:
    p = Path(image_path)
    try:
        img = safe_imread(p)
    except FileNotFoundError as e:
        return {"gan_artifacts": {"status": "error", "artifact_score": 0.0, "details": {"texture_repetition": 0.0, "sampling_artifacts": 0.0, "upscale_traces": 0.0, "pattern_periodicity": 0.0}, "notes": str(e)}} 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ml = MLWrapper()
    fat_score = ml.fatformer_score(img)
    man_heat_b64, man_score = ml.mantranet_heat_and_score(img)
    noise_score = ml.noiseprint_score(img)
    jpeg_flag = is_jpeg(p)
    jpeg_artifact_strength = estimate_jpeg_compression_artifact_strength(p)
    blur_var = variance_of_laplacian(gray)
    blur_score = float(np.clip(1.0 - (blur_var / (blur_var + 100.0)), 0.0, 1.0))
    portrait_like = detect_portrait_like(gray, img)
    architecture_strength = detect_architecture_pattern(gray)
    classical_texture = improved_texture_repetition_score(gray)
    classical_sampling = improved_sampling_artifacts_score(gray)
    classical_upscale = improved_upscale_traces_score(gray)
    classical_periodicity = improved_pattern_periodicity_score(gray)
    texture_score = None
    sampling_score = None
    upscale_score = None
    periodicity_score = None
    heatmap = None
    if fat_score is not None:
        texture_score = float(np.clip(fat_score, 0.0, 1.0))
    else:
        texture_score = float(np.clip(classical_texture, 0.0, 1.0))
    if noise_score is not None:
        sampling_score = float(np.clip(noise_score, 0.0, 1.0))
    else:
        sampling_score = float(np.clip(classical_sampling, 0.0, 1.0))
    if WEIGHTS["realesrgan_x4"].exists():
        try:
            h, w = img.shape[:2]
            down = cv2.resize(img, (max(8, w//2), max(8, h//2)), interpolation=cv2.INTER_AREA)
            up = cv2.resize(down, (w, h), interpolation=cv2.INTER_CUBIC)
            lap_o = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), cv2.CV_32F)
            lap_u = cv2.Laplacian(cv2.cvtColor(up, cv2.COLOR_BGR2GRAY).astype(np.float32), cv2.CV_32F)
            diff = np.abs(lap_o - lap_u)
            upscale_score = float(np.clip(float(np.mean(diff) / (np.mean(diff) + 8.0)), 0.0, 1.0))
            heatmap = safe_heatmap_and_b64(diff, CKPT_DIR / "realesrgan_diff.jpg")
        except Exception:
            upscale_score = float(np.clip(classical_upscale, 0.0, 1.0))
    else:
        upscale_score = float(np.clip(classical_upscale, 0.0, 1.0))
    if man_score is not None:
        periodicity_score = float(np.clip(man_score, 0.0, 1.0))
        if man_heat_b64 is not None:
            heatmap = man_heat_b64
    else:
        periodicity_score = float(np.clip(classical_periodicity, 0.0, 1.0))
    if jpeg_flag:
        jpeg_damp = 0.6 + 0.4 * (1.0 - jpeg_artifact_strength)
        texture_score = float(texture_score * jpeg_damp)
        periodicity_score = float(periodicity_score * jpeg_damp)
        sampling_score = float(sampling_score * (0.7 + 0.3 * (1.0 - jpeg_artifact_strength)))
    if architecture_strength > 0.4:
        texture_score = float(texture_score * (0.5 + 0.5 * (1.0 - architecture_strength)))
        periodicity_score = float(periodicity_score * (0.5 + 0.5 * (1.0 - architecture_strength)))
    if portrait_like:
        texture_score = float(texture_score * 0.7)
        periodicity_score = float(periodicity_score * 0.7)
    if blur_score > 0.6:
        sampling_score = float(sampling_score * 0.7)
        texture_score = float(texture_score * 0.85)
    texture_score = float(np.clip(texture_score, 0.0, 1.0))
    sampling_score = float(np.clip(sampling_score, 0.0, 1.0))
    upscale_score = float(np.clip(upscale_score, 0.0, 1.0))
    periodicity_score = float(np.clip(periodicity_score, 0.0, 1.0))
    ml_available = any(WEIGHTS[k].exists() for k in ("fatformer", "mantranet", "noiseprint"))
    if ml_available:
        w_ml = 0.70
        w_class = 0.30
    else:
        w_ml = 0.35
        w_class = 0.65
    combined_texture = texture_score * w_ml + classical_texture * (1.0 - w_ml)
    combined_sampling = sampling_score * w_ml + classical_sampling * (1.0 - w_ml)
    combined_upscale = upscale_score
    combined_periodicity = periodicity_score * w_ml + classical_periodicity * (1.0 - w_ml)
    artifact_score = round(float(combined_texture * 0.30 + combined_sampling * 0.30 + combined_upscale * 0.20 + combined_periodicity * 0.20), 4)
    result = {"gan_artifacts": {"status": "ok", "artifact_score": artifact_score, "details": {"texture_repetition": round(float(combined_texture), 4), "sampling_artifacts": round(float(combined_sampling), 4), "upscale_traces": round(float(combined_upscale), 4), "pattern_periodicity": round(float(combined_periodicity), 4)}, "notes": ""}}
    missing = []
    for k in ("fatformer", "mantranet", "noiseprint", "realesrgan_x4"):
        if not WEIGHTS[k].exists():
            missing.append(k)
    if missing:
        notes = []
        if "fatformer" in missing:
            notes.append("fatformer missing")
        if "mantranet" in missing:
            notes.append("mantranet missing")
        if "noiseprint" in missing:
            notes.append("noiseprint missing")
        if "realesrgan_x4" in missing:
            notes.append("realesrgan missing")
        result["gan_artifacts"]["notes"] = " | ".join(notes)
    # if heatmap is not None:
        # result["gan_artifacts"]["details"]["heatmap_preview"] = heatmap
    return result