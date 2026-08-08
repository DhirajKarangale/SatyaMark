import numpy as np
import cv2

def load_image_cv(image_bytes):
    """Converts raw bytes directly into OpenCV's grayscale format."""
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

def illumination_consistency(gray):
    """
    Calculates the direction of light gradients across the image.
    High variance means the light sources contradict each other.
    """
    # Calculate image gradients (edges and light falloff)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)

    # Calculate the angle of the light gradient for every pixel
    angles = np.arctan2(sobely, sobelx)

    # Split the image into 64x64 blocks to check local lighting
    h, w = gray.shape
    block_size = 64
    dominant_angles = []

    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            block_angles = angles[y:y+block_size, x:x+block_size]
            mean_angle = np.mean(block_angles)
            dominant_angles.append(mean_angle)

    # Measure how chaotic the lighting angles are globally
    variance = np.var(dominant_angles)
    
    return {
        "lighting_angle_variance": float(variance),
        # A simple normalized score: closer to 0 means chaotic AI lighting
        "lighting_consistency_score": float(1.0 / (1.0 + (variance / 10)))
    }

def vanishing_point_chaos(gray):
    """
    Detects straight lines and measures their angular grouping.
    AI struggles to maintain mathematically perfect parallel lines.
    """
    # Find sharp edges
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect straight lines mathematically
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is None or len(lines) < 2:
         return {"line_chaos_score": 0.0, "lines_detected": 0}

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Calculate the angle of the line
        angle = np.arctan2(y2 - y1, x2 - x1)
        angles.append(angle)

    # In natural architecture, lines group tightly into 1-3 vanishing points.
    # AI lines often have a higher spread (standard deviation).
    angle_std = np.std(angles)

    return {
        "line_chaos_score": float(angle_std),
        "lines_detected": len(lines)
    }

def process(image_bytes):
    try:
        gray = load_image_cv(image_bytes)
        
        illumination = illumination_consistency(gray)
        geometry = vanishing_point_chaos(gray)

        return {
            "physics_and_geometry": {
                "illumination": illumination,
                "perspective": geometry
            }
        }
    except Exception as e:
         return {"error": str(e)}