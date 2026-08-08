import numpy as np
import cv2

def load_image_cv(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return img.astype(np.float32)

def analyze_diffusion_latents(image_bytes):
    """
    Diffusion Latent Analysis
    Analyzes the statistical distribution of high-frequency noise.
    Diffusion images have 'perfect' Gaussian residuals.
    Real images have 'heavy-tailed' physical noise.
    """
    try:
        gray = load_image_cv(image_bytes)
        
        # 1. Extract High-Frequency Residuals (The 'Latent' Noise)
        # We use a Laplacian filter to remove the visual content
        laplacian = cv2.Laplacian(gray, cv2.CV_32F)
        
        # 2. Calculate Higher-Order Statistics
        # Mean and Std are too simple; we need Kurtosis and Skewness
        mu = np.mean(laplacian)
        sigma = np.std(laplacian)
        
        if sigma == 0:
            return {"error": "Image has no variance (solid color)"}
            
        # Kurtosis: Measures how 'Gaussian' the noise is.
        # Normal Gaussian distribution has a Kurtosis of ~3.0.
        kurtosis = np.mean(((laplacian - mu) / sigma) ** 4)
        
        # Skewness: Measures the asymmetry of the noise.
        skewness = np.mean(((laplacian - mu) / sigma) ** 3)
        
        # 3. Diffusion Alignment Logic
        # Diffusion models are trained to produce Gaussian noise (Kurtosis ~3).
        # Real camera sensor noise is 'impulsive' and 'heavy-tailed' (Kurtosis > 10).
        is_diffusion_aligned = bool(2.0 < kurtosis < 5.0)

        return {
            "latent_kurtosis": float(kurtosis),
            "latent_skewness": float(skewness),
            "diffusion_confidence_score": float(1.0 - (abs(kurtosis - 3.0) / 10.0)),
            "is_diffusion_aligned": is_diffusion_aligned
        }
    except Exception as e:
        return {"error": str(e)}

def process(image_bytes):
    return analyze_diffusion_latents(image_bytes)