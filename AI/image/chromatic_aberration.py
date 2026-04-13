import numpy as np
import cv2

def analyze_chromatic_aberration(image_bytes):
    """
    Measures the alignment of color channels (Red vs Blue).
    Real lenses show misalignment (aberration) at the edges.
    AI images remain perfectly aligned edge-to-edge.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"error": "Could not decode image"}

        h, w, _ = img.shape
        # OpenCV loads images in BGR format
        b, g, r = cv2.split(img)

        # Define the center and the top-left corner regions (10% of image size)
        cy, cx = h // 2, w // 2
        my, mx = h // 10, w // 10

        # Extract pixels and flatten to 1D arrays
        center_r = r[cy-my:cy+my, cx-mx:cx+mx].flatten()
        center_b = b[cy-my:cy+my, cx-mx:cx+mx].flatten()

        edge_r = r[0:my*2, 0:mx*2].flatten()
        edge_b = b[0:my*2, 0:mx*2].flatten()

        # Calculate Pearson correlation coefficient between Red and Blue
        # (How tightly matched the color channels are)
        if len(center_r) < 2 or len(edge_r) < 2:
            return {"error": "Image too small for optical analysis"}

        center_corr = np.corrcoef(center_r, center_b)[0, 1]
        edge_corr = np.corrcoef(edge_r, edge_b)[0, 1]

        # Handle NaNs (which happen if a region is perfectly flat, like a solid white wall)
        if np.isnan(center_corr): center_corr = 1.0
        if np.isnan(edge_corr): edge_corr = 1.0

        # Calculate the shift: natural photos lose correlation at the edges
        ca_shift = float(center_corr - edge_corr)

        return {
            "center_color_alignment": float(center_corr),
            "edge_color_alignment": float(edge_corr),
            "aberration_shift": ca_shift,
            # A shift > 0.015 generally indicates physical lens dispersion
            "has_natural_lens_dispersion": bool(ca_shift > 0.015) 
        }
    except Exception as e:
        return {"error": str(e)}

def process(image_bytes):
    return analyze_chromatic_aberration(image_bytes)