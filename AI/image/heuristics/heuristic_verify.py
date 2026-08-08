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

def verify(img):
    try:
        image_bytes = img["bytes"]
        pil_image = img["pil_image"]
        gray_pixels = img["pixels_gray"]

        img_metadata = metadata.process(image_bytes)
        img_c2pa = c2pa.process(image_bytes)
        img_watermark = watermark.process(image_bytes)
        img_visual_artifacts = visual_artifacts.process(pil_image)
        img_frequency_domain_analysis = frequency_domain_analysis.process(image_bytes)
        img_pixel_level_analysis = pixel_level_analysis.process(image_bytes)
        img_sensor_pattern_noise = sensor_pattern_noise.process(gray_pixels)
        img_compression_artifact_analysis = compression_artifact_analysis.process(image_bytes)
        img_gan = gan.process(image_bytes)
        img_perturbation_robustness_testing = perturbation_robustness_testing.process(image_bytes)
        img_physics_geometry = physics_geometry.process(image_bytes)
        img_ela_analysis = ela_analysis.process(image_bytes)
        img_autoencoder_reconstruction = autoencoder_reconstruction.process(image_bytes)
        img_diffusion_latent_analysis = diffusion_latent_analysis.process(image_bytes)
        img_benfords_law = benfords_law.process(image_bytes)
        img_chromatic_aberration = chromatic_aberration.process(image_bytes)
        img_patch_analysis = patch_analyzer.process(image_bytes)
        img_copy_move = copy_move.process(image_bytes)
    
        data = {
            "metadata": img_metadata,
            "c2pa": img_c2pa,
            "watermark": img_watermark,
            "visual": img_visual_artifacts,
            "frequency_domain_analysis": img_frequency_domain_analysis,
            "pixel": img_pixel_level_analysis,
            "sensor_pattern_noise": img_sensor_pattern_noise,
            "compression_artifact_analysis": img_compression_artifact_analysis,
            "gan": img_gan,
            "perturbation": img_perturbation_robustness_testing,
            "physics_geometry": img_physics_geometry,
            "ela_analysis": img_ela_analysis,
            "autoencoder_reconstruction": img_autoencoder_reconstruction,
            "diffusion_latent_analysis": img_diffusion_latent_analysis,
            "benfords_law": img_benfords_law,
            "chromatic_aberration": img_chromatic_aberration,
            "patch_analysis": img_patch_analysis,
            "copy_move": img_copy_move
        }

        img_decision_engine = decision_engine.process(data) 
        return img_decision_engine

    except Exception as e:
        logger.error(f"Heuristic verification failed: {e}", exc_info=True)
        return {
            "mark": "ERROR",
            "confidence": 0,
            "reason": f"Heuristic pipeline failed: {str(e)}"
        }
