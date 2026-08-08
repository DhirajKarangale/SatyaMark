import numpy as np
import cv2

def load_image_cv(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    # Resize to a standard 256x256 for consistent math
    return cv2.resize(img, (256, 256))

def simulate_reconstruction(image_bytes, compression_rank=20):
    """
    Simulates Autoencoder Reconstruction Error using SVD.
    Real photos have high 'rank' (complex noise).
    AI photos have low 'rank' (mathematical patterns).
    """
    try:
        gray = load_image_cv(image_bytes).astype(np.float32)
        
        # 1. Perform Singular Value Decomposition (The 'Encoder' step)
        U, S, Vt = np.linalg.svd(gray, full_matrices=False)
        
        # 2. Keep only the top 'k' singular values (The 'Bottleneck' step)
        # SVD rank-k approximation mimics an autoencoder's latent space.
        S_compressed = np.zeros_like(S)
        S_compressed[:compression_rank] = S[:compression_rank]
        
        # 3. Reconstruct the image (The 'Decoder' step)
        reconstructed = np.dot(U, np.dot(np.diag(S_compressed), Vt))
        
        # 4. Calculate Reconstruction Error (MSE)
        error = np.mean((gray - reconstructed) ** 2)
        
        # 5. Normalized Anomaly Score
        # Real images usually have error > 100 due to complex sensor noise.
        # AI images are often 'simpler' and score < 50.
        return {
            "reconstruction_error": float(error),
            "compression_rank": compression_rank,
            "is_suspiciously_simple": bool(error < 60.0)
        }
    except Exception as e:
        return {"error": str(e)}

def process(image_bytes):
    return simulate_reconstruction(image_bytes)