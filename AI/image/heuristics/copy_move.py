import numpy as np
import cv2

def load_image_cv(image_bytes):
    img_array = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

def analyze_copy_move(image_bytes, block_size=16, stride=8):
    """
    Hunts for identical pixel blocks within the same image.
    Catches Photoshop 'Clone Stamp' tampering and AI texture tiling.
    """
    try:
        gray = load_image_cv(image_bytes)
        if gray is None:
            return {"error": "Could not decode image"}
            
        h, w = gray.shape
        
        # 1. Extract feature vectors for every block
        blocks = []
        for y in range(0, h - block_size, stride):
            for x in range(0, w - block_size, stride):
                block = gray[y:y+block_size, x:x+block_size]
                # The fingerprint: [Mean, Std Dev, Y-Coord, X-Coord]
                fingerprint = [np.mean(block), np.std(block), y, x]
                blocks.append(fingerprint)
        
        if not blocks:
            return {"error": "Image too small"}

        # 2. Sort blocks by their mathematical fingerprints
        blocks = np.array(blocks)
        # Sort by Mean, then by Std Dev
        sorted_indices = np.lexsort((blocks[:, 1], blocks[:, 0]))
        sorted_blocks = blocks[sorted_indices]
        
        # 3. Check adjacent blocks in the sorted list for exact matches
        matches = 0
        for i in range(len(sorted_blocks) - 1):
            # If the block fingerprints are nearly identical
            if abs(sorted_blocks[i, 0] - sorted_blocks[i+1, 0]) < 0.5:
                if abs(sorted_blocks[i, 1] - sorted_blocks[i+1, 1]) < 0.5:
                    # Check physical distance (ignore blocks that are just touching)
                    dist = np.sqrt((sorted_blocks[i, 2] - sorted_blocks[i+1, 2])**2 + 
                                   (sorted_blocks[i, 3] - sorted_blocks[i+1, 3])**2)
                    if dist > block_size * 2:
                        matches += 1

        match_ratio = matches / len(blocks)
        
        return {
            "patch_matches_found": matches,
            "tiling_artifact_score": float(match_ratio),
            # If more than 2% of the image consists of distant clone twins
            "is_copy_move_detected": bool(match_ratio > 0.02)
        }
    except Exception as e:
        return {"error": str(e)}

def process(image_bytes):
    return analyze_copy_move(image_bytes)