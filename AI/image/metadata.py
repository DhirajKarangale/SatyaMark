import contextlib
import io
import json
import re
from io import BytesIO
from PIL import Image
import piexif
import exifread


GENERATOR_SIGNATURES = [
    "stable diffusion","automatic1111","comfyui","invokeai","novelai",
    "midjourney","dalle","openai","firefly","runway","leonardo ai",
    "playground ai","clipdrop","dreamstudio","bing image creator"
]


KNOWN_CAMERA_BRANDS = [
    "canon","nikon","sony","fujifilm","panasonic","leica",
    "olympus","hasselblad","pentax","apple","samsung","google"
]


GENERATION_PATTERNS = [
    r"steps:\s*\d+",
    r"sampler:\s*\w+",
    r"cfg scale:\s*\d+",
    r"seed:\s*\d+",
    r"model:\s*[\w\-.]+",
    r"negative prompt:",
    r"size:\s*\d+x\d+",
]


def extract_basic_metadata(image):

    return {
        "format": image.format,
        "mode": image.mode,
        "width": image.width,
        "height": image.height,
        "bands": image.getbands(),
        "info_keys": list(image.info.keys()),
        "dpi": image.info.get("dpi"),
        "gamma": image.info.get("gamma"),
        "compression": image.info.get("compression"),
        "icc_profile_present": "icc_profile" in image.info,
    }


def extract_pillow_metadata(image):

    metadata = {}

    for k, v in image.info.items():
        try:
            metadata[k] = str(v)
        except:
            metadata[k] = "unreadable"

    return metadata


def extract_exif_piexif(image):

    data = {}

    try:

        exif_dict = piexif.load(image.info.get("exif", b""))

        for section in exif_dict:

            if isinstance(exif_dict[section], dict):

                for tag, value in exif_dict[section].items():

                    try:
                        data[f"{section}_{tag}"] = str(value)
                    except:
                        data[f"{section}_{tag}"] = "unreadable"

    except:
        pass

    return data


def extract_exif_exifread(image_bytes):

    tags = {}

    try:

        f = BytesIO(image_bytes)

        # exif = exifread.process_file(f, details=True)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            exif = exifread.process_file(f, details=True)

        for tag in exif:

            try:
                tags[tag] = str(exif[tag])
            except:
                tags[tag] = "unreadable"

    except:
        pass

    return tags


def detect_generator_signatures(text_blob):

    found = []

    for sig in GENERATOR_SIGNATURES:

        if sig in text_blob:
            found.append(sig)

    return found


def detect_generation_parameters(text_blob):

    found = []

    for pattern in GENERATION_PATTERNS:

        if re.search(pattern, text_blob):
            found.append(pattern)

    return found


def detect_camera_validity(text_blob):

    for brand in KNOWN_CAMERA_BRANDS:

        if brand in text_blob:
            return True

    return False


def scan_raw_metadata(image_bytes):

    try:

        raw = image_bytes.decode("latin1", errors="ignore").lower()

    except:

        raw = ""

    return raw


def metadata_analysis(image_bytes):

    image = Image.open(BytesIO(image_bytes))

    basic = extract_basic_metadata(image)

    pillow_meta = extract_pillow_metadata(image)

    exif_piexif = extract_exif_piexif(image)

    exif_exifread = extract_exif_exifread(image_bytes)

    raw_scan = scan_raw_metadata(image_bytes)

    combined_text = json.dumps({
        "pillow": pillow_meta,
        "piexif": exif_piexif,
        "exifread": exif_exifread,
    }).lower() + raw_scan

    generator_signatures = detect_generator_signatures(combined_text)

    generation_parameters = detect_generation_parameters(combined_text)

    camera_valid = detect_camera_validity(combined_text)

    issues = []

    if not exif_piexif and not exif_exifread:
        issues.append("missing_exif")

    if not camera_valid:
        issues.append("no_camera_signature")

    if "software" in combined_text:
        if any(x in combined_text for x in ["photoshop","gimp","ai","diffusion"]):
            issues.append("editing_or_ai_software")

    analysis = {
        "has_exif": bool(exif_piexif or exif_exifread),
        "camera_valid": camera_valid,
        "generator_signatures": generator_signatures,
        "generation_parameters_detected": generation_parameters,
        "consistency_issues": issues,
        "suspicious": bool(generator_signatures or generation_parameters),
    }

    result = {
        "basic_metadata": basic,
        "pillow_metadata": pillow_meta,
        "exif_piexif": exif_piexif,
        "exif_exifread": exif_exifread,
        "analysis": analysis,
    }

    return result


def process(image_bytes):
    result = metadata_analysis(image_bytes)
    # return json.dumps(result, indent=2)
    return result