import logging
from . import metadata
from . import c2pa
from . import watermark 
from . import visual_artifacts
from . import frequency_domain_analysis
from . import pixel_level_analysis
from . import sensor_pattern_noise
from . import compression_artifact_analysis
from . import gan
from . import perturbation_robustness_testing
from . import physics_geometry
from . import ela_analysis
from . import autoencoder_reconstruction
from . import diffusion_latent_analysis
from . import benfords_law
from . import chromatic_aberration
from . import patch_analyzer
from . import copy_move
from . import decision_engine

logger = logging.getLogger(__name__)

import concurrent.futures

def run_heuristics(img):
    image_bytes = img["bytes"]
    pil_image = img["pil_image"]
    gray_pixels = img["pixels_gray"]
    
    tasks = {
        "metadata": lambda: metadata.process(image_bytes),
        "c2pa": lambda: c2pa.process(image_bytes),
        "watermark": lambda: watermark.process(image_bytes),
        "visual": lambda: visual_artifacts.process(pil_image),
        "frequency_domain_analysis": lambda: frequency_domain_analysis.process(image_bytes),
        "pixel": lambda: pixel_level_analysis.process(image_bytes),
        "sensor_pattern_noise": lambda: sensor_pattern_noise.process(gray_pixels),
        "compression_artifact_analysis": lambda: compression_artifact_analysis.process(image_bytes),
        "gan": lambda: gan.process(image_bytes),
        "perturbation": lambda: perturbation_robustness_testing.process(image_bytes),
        "physics_geometry": lambda: physics_geometry.process(image_bytes),
        "ela_analysis": lambda: ela_analysis.process(image_bytes),
        "autoencoder_reconstruction": lambda: autoencoder_reconstruction.process(image_bytes),
        "diffusion_latent_analysis": lambda: diffusion_latent_analysis.process(image_bytes),
        "benfords_law": lambda: benfords_law.process(image_bytes),
        "chromatic_aberration": lambda: chromatic_aberration.process(image_bytes),
        "patch_analysis": lambda: patch_analyzer.process(image_bytes),
        "copy_move": lambda: copy_move.process(image_bytes)
    }

    data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_name = {executor.submit(func): name for name, func in tasks.items()}
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                data[name] = future.result()
            except Exception as e:
                logger.error(f"Heuristic {name} failed: {e}")
                data[name] = {}
                
    return data


def verify(img):
    try:
        data = run_heuristics(img)
        img_decision_engine = decision_engine.process(data) 
        return img_decision_engine

    except Exception as e:
        logger.error(f"Heuristic verification failed: {e}", exc_info=True)
        return {
            "mark": "ERROR",
            "confidence": 0,
            "reason": f"Heuristic pipeline failed: {str(e)}"
        }
