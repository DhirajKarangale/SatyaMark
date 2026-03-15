import json


def parse_jpeg_segments(data):
    i = 2  # skip SOI
    segments = []

    while i < len(data):
        if data[i] != 0xFF:
            break

        marker = data[i + 1]
        i += 2

        # EOI
        if marker == 0xD9:
            break

        # markers without length
        if marker in (0x01,) or (0xD0 <= marker <= 0xD7):
            continue

        length = int.from_bytes(data[i:i+2], "big")
        segment_data = data[i+2:i+length]

        segments.append({
            "marker": marker,
            "data": segment_data
        })

        i += length

    return segments


def detect_c2pa_jumbf(segment_data):
    # JUMBF box signature
    if b"jumb" in segment_data or b"uuid" in segment_data:
        if b"c2pa" in segment_data:
            return True
    return False


def c2pa_analysis(image_bytes):

    try:

        # check JPEG
        if not image_bytes.startswith(b"\xff\xd8"):
            return {
                "c2pa_present": False,
                "valid_signature": None,
                "reason": "Not JPEG container"
            }

        segments = parse_jpeg_segments(image_bytes)

        for seg in segments:

            # APP11 is where JUMBF is usually stored
            if seg["marker"] == 0xEB:

                if detect_c2pa_jumbf(seg["data"]):
                    return {
                        "c2pa_present": True,
                        "valid_signature": None,
                        "container": "JPEG",
                        "segment": "APP11"
                    }

        result = {
            "c2pa_present": False,
            "valid_signature": None
        }
    
        return result

    except Exception as e:
        return {
            "c2pa_present": False,
            "valid_signature": False,
            "error": str(e)
        }


def process(image_bytes):
    result = c2pa_analysis(image_bytes)
    # return json.dumps(result, indent=2)
    return result