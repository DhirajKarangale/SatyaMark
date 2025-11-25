import os
import tempfile
import imghdr
from urllib.parse import urlparse

import requests
from PIL import Image

from AI.img_forensic.img_forensic_watermark_signature import watermark_analyze
from AI.img_forensic.img_forensic_sensor_fingerprint import sensor_fingerprint_analyze
from AI.img_forensic.img_forensic_gan_artifacts import gan_artifacts_analyze
from AI.img_forensic.img_forensic_local_manipulation import local_manipulation_analyze
from AI.img_forensic.img_forensic_metadata import metadata_analysis
from AI.img_forensic.img_forensic_semantic_consistency import semantic_consistency_analyze
from AI.img_forensic.img_forensic_forensic_decision import classify_image

timeout: int = 10
max_bytes: int = 5 * 1024 * 1024


def analyze_image_from_url(url: str):
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.netloc:
            return {"error": "Invalid URL"}
    except Exception:
        return {"error": "Invalid URL"}

    temp_path = None
    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name
            downloaded = 0
            for chunk in resp.iter_content(8192):
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > max_bytes:
                    return {"error": "File too large"}
                tmp.write(chunk)

        kind = imghdr.what(temp_path)
        if kind is None:
            try:
                with Image.open(temp_path) as im:
                    im.verify()
            except:
                return {"error": "Downloaded file is not an image"}

        w = watermark_analyze(temp_path)
        s = sensor_fingerprint_analyze(temp_path)
        g = gan_artifacts_analyze(temp_path)
        l = local_manipulation_analyze(temp_path)
        m = metadata_analysis(temp_path)
        sc = semantic_consistency_analyze(temp_path)

        final_result = classify_image(w, s, g, l, m, sc)

        return final_result

    except Exception as e:
        return {"error": str(e)}

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


if __name__ == "__main__":
    url = "https://picsum.photos/seed/picsum/200/300"
    result = analyze_image_from_url(url)
    print(result)
