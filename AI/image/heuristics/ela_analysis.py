import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from io import BytesIO

def perform_ela(image_bytes, quality=90):
    """
    Error Level Analysis (ELA)
    Checks for inconsistent compression levels. 
    Digital edits or AI 'pastes' stand out as brighter areas.
    """
    try:
        # 1. Load the original image
        original = Image.open(BytesIO(image_bytes)).convert('RGB')
        
        # 2. Resave it at a known quality (temporary buffer)
        temp_buffer = BytesIO()
        original.save(temp_buffer, format='JPEG', quality=quality)
        temp_buffer.seek(0)
        resaved = Image.open(temp_buffer)
        
        # 3. Find the mathematical difference between Original and Resaved
        # Areas with consistent compression will be dark. 
        # Edited/AI areas will appear as bright 'noise'.
        ela_im = ImageChops.difference(original, resaved)
        
        # 4. Enhance the brightness so the human eye (and our engine) can see it
        extrema = ela_im.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        
        ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)
        
        # 5. Convert to stats
        ela_data = np.array(ela_im)
        mean_diff = np.mean(ela_data)
        max_diff_val = np.max(ela_data)
        std_diff = np.std(ela_data)

        return {
            "ela_score": float(mean_diff),
            "ela_max_variation": float(max_diff_val),
            "ela_std_deviation": float(std_diff),
            "is_suspicious": bool(mean_diff > 15.0 or std_diff > 20.0)
        }
    except Exception as e:
        return {"error": str(e)}

def process(image_bytes):
    return perform_ela(image_bytes)