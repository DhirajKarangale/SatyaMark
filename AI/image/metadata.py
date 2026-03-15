import json
import re
import struct
import contextlib
import io
from io import BytesIO
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


def detect_format(image_bytes):

    if image_bytes.startswith(b"\x89PNG"):
        return "PNG"

    if image_bytes.startswith(b"\xff\xd8"):
        return "JPEG"

    return "UNKNOWN"


def parse_png_metadata(image_bytes):

    width = None
    height = None
    metadata = {}

    stream = BytesIO(image_bytes)

    stream.read(8)  # skip signature

    while True:

        chunk_len_bytes = stream.read(4)

        if not chunk_len_bytes:
            break

        chunk_len = struct.unpack(">I", chunk_len_bytes)[0]

        chunk_type = stream.read(4).decode("latin1")

        chunk_data = stream.read(chunk_len)

        stream.read(4)  # CRC

        if chunk_type == "IHDR":
            width, height = struct.unpack(">II", chunk_data[:8])

        elif chunk_type in ["tEXt", "iTXt", "zTXt"]:

            try:
                text = chunk_data.decode("latin1", errors="ignore")
                key_val = text.split("\x00", 1)

                if len(key_val) == 2:
                    metadata[key_val[0]] = key_val[1]
            except:
                pass

        elif chunk_type == "sRGB":
            metadata["srgb"] = chunk_data[0]

        elif chunk_type == "gAMA":
            gamma = struct.unpack(">I", chunk_data)[0]
            metadata["gamma"] = gamma

        elif chunk_type == "pHYs":
            x, y, unit = struct.unpack(">IIB", chunk_data)
            metadata["dpi"] = [x, y]

        if chunk_type == "IEND":
            break

    return width, height, metadata


def parse_jpeg_size(image_bytes):

    stream = BytesIO(image_bytes)

    stream.read(2)

    while True:

        marker, = struct.unpack("B", stream.read(1))

        if marker != 0xFF:
            continue

        code, = struct.unpack("B", stream.read(1))

        if code in [0xC0, 0xC2]:

            stream.read(3)

            height, width = struct.unpack(">HH", stream.read(4))

            return width, height

        else:

            size, = struct.unpack(">H", stream.read(2))

            stream.read(size - 2)


def extract_exif(image_bytes):

    tags = {}

    try:

        f = BytesIO(image_bytes)

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            exif = exifread.process_file(f, details=True)

        for tag in exif:
            tags[tag] = str(exif[tag])

    except:
        pass

    return tags


def scan_raw_metadata(image_bytes):

    try:
        return image_bytes.decode("latin1", errors="ignore").lower()
    except:
        return ""


def detect_generator_signatures(text_blob):

    return [sig for sig in GENERATOR_SIGNATURES if sig in text_blob]


def detect_generation_parameters(text_blob):

    return [p for p in GENERATION_PATTERNS if re.search(p, text_blob)]


def detect_camera_validity(text_blob):

    return any(b in text_blob for b in KNOWN_CAMERA_BRANDS)


def metadata_analysis(image_bytes):

    fmt = detect_format(image_bytes)

    width = None
    height = None
    metadata = {}

    if fmt == "PNG":
        width, height, metadata = parse_png_metadata(image_bytes)

    elif fmt == "JPEG":
        width, height = parse_jpeg_size(image_bytes)

    exif = extract_exif(image_bytes)

    raw_scan = scan_raw_metadata(image_bytes)

    combined_text = json.dumps({
        "metadata": metadata,
        "exif": exif
    }).lower() + raw_scan

    generator_signatures = detect_generator_signatures(combined_text)

    generation_parameters = detect_generation_parameters(combined_text)

    camera_valid = detect_camera_validity(combined_text)

    issues = []

    if not exif:
        issues.append("missing_exif")

    if not camera_valid:
        issues.append("no_camera_signature")

    analysis = {
        "has_exif": bool(exif),
        "camera_valid": camera_valid,
        "generator_signatures": generator_signatures,
        "generation_parameters_detected": generation_parameters,
        "consistency_issues": issues,
        "suspicious": bool(generator_signatures or generation_parameters),
    }

    return {
        "basic_metadata": {
            "format": fmt,
            "width": width,
            "height": height
        },
        "embedded_metadata": metadata,
        "exif": exif,
        "analysis": analysis
    }


def process(image_bytes):
    result = metadata_analysis(image_bytes)
    # return json.dumps(result, indent=2)
    return result