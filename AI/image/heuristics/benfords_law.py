import numpy as np
import cv2

def get_dct_coefficients(image_bytes):
    """Extracts raw DCT coefficients from the image."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Ensure image size is a perfect multiple of 8 for DCT blocks
    h, w = img.shape
    img = img[:h//8*8, :w//8*8].astype(np.float32)
    
    coeffs = []
    # Break image into 8x8 pixel blocks
    for i in range(0, img.shape[0], 8):
        for j in range(0, img.shape[1], 8):
            block = img[i:i+8, j:j+8]
            dct_block = cv2.dct(block)
            # Flatten the block and add to our list of coefficients
            coeffs.extend(dct_block.flatten())
            
    return np.array(coeffs)

def analyze_benfords_law(image_bytes):
    """
    Analyzes if the DCT coefficients follow the natural Benford curve.
    AI and heavy editing disrupt this statistical distribution.
    """
    try:
        coeffs = get_dct_coefficients(image_bytes)
        
        # Filter for non-zero coefficients and get the absolute first digit
        abs_coeffs = np.abs(coeffs)
        first_digits = []
        
        for val in abs_coeffs:
            if val > 0:
                # Convert to string, remove decimals, remove leading zeros
                s = str(val).replace('.', '').lstrip('0')
                if s:
                    first_digits.append(int(s[0]))
        
        if not first_digits:
            return {"error": "No significant coefficients found"}

        # Calculate actual frequencies of digits 1 through 9
        counts = np.bincount(first_digits)[1:10]
        actual_dist = counts / len(first_digits)
        
        # Ideal Benford Distribution formula: P(d) = log10(1 + 1/d)
        ideal_dist = np.array([np.log10(1 + 1/d) for d in range(1, 10)])
        
        # Calculate Chi-Square distance (Lower is better/more natural)
        chi_square_stat = np.sum(((actual_dist - ideal_dist)**2) / ideal_dist)

        return {
            "benford_chi_square": float(chi_square_stat),
            "actual_distribution": actual_dist.tolist(),
            "ideal_distribution": ideal_dist.tolist(),
            # A threshold of 0.05 is generally safe for natural JPEGs
            "is_statistically_natural": bool(chi_square_stat < 0.05)
        }
    except Exception as e:
        return {"error": str(e)}

def process(image_bytes):
    return analyze_benfords_law(image_bytes)