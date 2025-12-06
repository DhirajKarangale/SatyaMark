import piexif
from PIL import Image
import os


def metadata_analysis(image_path):
    result = {
        "exif_analysis": {
            "status": "ok",
            "has_exif": False,
            "camera_data_present": False,
            "details": {
                "camera_make": None,
                "camera_model": None,
                "software": None,
                "timestamp": None,
                "gps": None,
                "inconsistencies": [],
            },
            "notes": "",
        }
    }

    if not os.path.exists(image_path):
        result["exif_analysis"]["status"] = "error"
        result["exif_analysis"]["notes"] = "File not found"
        return result

    try:
        img = Image.open(image_path)

        try:
            exif_dict = piexif.load(img.info.get("exif", b""))
        except Exception:
            result["exif_analysis"]["status"] = "not_found"
            return result

        if not exif_dict or all(len(exif_dict[k]) == 0 for k in exif_dict):
            result["exif_analysis"]["status"] = "not_found"
            return result

        result["exif_analysis"]["has_exif"] = True

        make = exif_dict["0th"].get(piexif.ImageIFD.Make)
        model = exif_dict["0th"].get(piexif.ImageIFD.Model)

        software = exif_dict["0th"].get(piexif.ImageIFD.Software)

        timestamp = exif_dict["0th"].get(piexif.ImageIFD.DateTime)

        gps = exif_dict.get("GPS", {})
        gps_present = len(gps.keys()) > 0

        result["exif_analysis"]["camera_data_present"] = bool(make or model)

        result["exif_analysis"]["details"]["camera_make"] = (
            make.decode() if make else None
        )
        result["exif_analysis"]["details"]["camera_model"] = (
            model.decode() if model else None
        )
        result["exif_analysis"]["details"]["software"] = (
            software.decode() if software else None
        )
        result["exif_analysis"]["details"]["timestamp"] = (
            timestamp.decode() if timestamp else None
        )
        result["exif_analysis"]["details"]["gps"] = True if gps_present else None

        inconsistencies = []

        if result["exif_analysis"]["has_exif"]:
            sw = result["exif_analysis"]["details"]["software"]
            if sw and any(
                x in sw.lower() for x in ["photoshop", "ai", "midjourney", "diffusion"]
            ):
                inconsistencies.append(
                    "Software indicates post-processing or AI generation"
                )

        if timestamp and (not make and not model):
            inconsistencies.append("Timestamp exists but no camera make/model")

        result["exif_analysis"]["details"]["inconsistencies"] = inconsistencies

        return result

    except Exception as e:
        result["exif_analysis"]["status"] = "error"
        result["exif_analysis"]["notes"] = str(e)
        return result
