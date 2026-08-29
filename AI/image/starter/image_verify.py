import logging
import os
from image import downloader
from image.heuristics import heuristic_verify
from image.sightengine import sightengine_verify
from image.truthscan import truthscan_verify

logger = logging.getLogger(__name__)

VERIFICATION_PIPELINE = ['truthscan', 'sightengine', 'heuristic']

def verify(image_source):
    try:
        if os.path.exists(image_source):
            img = downloader.process_local(image_source)
        else:
            img = downloader.process(image_source)
            
        last_error_reason = ""
        
        for method in VERIFICATION_PIPELINE:
            logger.info(f"Trying verification method: {method}")
            
            if method == 'sightengine':
                result = sightengine_verify.verify(img)
            elif method == 'truthscan':
                result = truthscan_verify.verify(img)
            elif method == 'heuristic':
                result = heuristic_verify.verify(img)
            else:
                logger.warning(f"Unknown verification method: {method}")
                continue
                
            if result.get("mark") != "ERROR":
                return result
                
            logger.warning(f"Method {method} failed: {result.get('reason')}. Falling back to next method...")
            last_error_reason = result.get('reason')
            
        return {
            "mark": "ERROR",
            "confidence": 0,
            "reason": f"All verification methods in the pipeline failed. Last error: {last_error_reason}"
        }

    except Exception as e:
        logger.error(f"Image verification failed for {image_source}: {e}", exc_info=True)
        return {
            "mark": "ERROR",
            "confidence": 0,
            "reason": f"Verification pipeline encountered a critical error: {str(e)}"
        }
