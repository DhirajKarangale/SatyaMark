import numpy as np
import cv2

def load_image_cv(image_bytes):
    img_array = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

def detect_copy_move(image_bytes, block_size=16):
    """
    Patch-Based Detection: Hunts for identical or near-identical 
    pixel blocks within the same image (Copy-Paste Forgery).
    """
    try:
        gray = load_image_cv(image_bytes)
        h, w = gray.shape
        
        # 1. Extract feature vectors for every block
        blocks = []
        for y in range(0, h - block_size, 4): # Stride of 4 for speed
            for x in range(0, w - block_size, 4):
                block = gray[y:y+block_size, x:x+block_size]
                # Mean and variance serve as a simple 'fingerprint'
                fingerprint = [np.mean(block), np.std(block), y, x]
                blocks.append(fingerprint)
        
        # 2. Sort blocks by their fingerprints to find 'twins' instantly
        blocks = np.array(blocks)
        sorted_indices = np.lexsort((blocks[:, 1], blocks[:, 0]))
        sorted_blocks = blocks[sorted_indices]
        
        # 3. Check adjacent blocks in the sorted list for matches
        matches = 0
        for i in range(len(sorted_blocks) - 1):
            if abs(sorted_blocks[i, 0] - sorted_blocks[i+1, 0]) < 0.1:
                if abs(sorted_blocks[i, 1] - sorted_blocks[i+1, 1]) < 0.1:
                    # Check physical distance (ignore touching blocks like solid skies)
                    dist = np.sqrt((sorted_blocks[i, 2] - sorted_blocks[i+1, 2])**2 + 
                                   (sorted_blocks[i, 3] - sorted_blocks[i+1, 3])**2)
                    if dist > block_size * 2:
                        matches += 1

        match_ratio = matches / len(blocks)
        
        return {
            "patch_matches_found": matches,
            "tiling_artifact_score": float(match_ratio),
            "is_suspicious": bool(match_ratio > 0.05) # >5% cloned blocks
        }
    except Exception as e:
        return {"error": str(e)}

def process(image_bytes):
    return detect_copy_move(image_bytes)