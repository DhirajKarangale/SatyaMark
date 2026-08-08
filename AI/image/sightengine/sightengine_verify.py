import logging
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_api_credentials():
    users_env = os.getenv("SIGHTENGINE_API_USERS", "")
    secrets_env = os.getenv("SIGHTENGINE_API_SECRET", "")
    
    users = [u.strip() for u in users_env.split(",") if u.strip()]
    secrets = [s.strip() for s in secrets_env.split(",") if s.strip()]
    
    return list(zip(users, secrets))

def verify(img):
    try:
        image_bytes = img.get("bytes")
        if not image_bytes:
            raise ValueError("No image bytes provided in the img dictionary.")
            
        credentials = get_api_credentials()
        if not credentials:
            raise ValueError("No Sightengine API credentials found in environment variables.")
        
        max_retries = int(os.getenv("EXPONENTIAL_BACKOFF_MAX_RETRIES", "3"))
        base_time = int(os.getenv("EXPONENTIAL_BACKOFF_BASE_TIME", "2"))
        
        last_error = None
        
        for api_user, api_secret in credentials:
            for attempt in range(max_retries + 1):
                try:
                    params = {
                        'models': 'genai',
                        'api_user': api_user,
                        'api_secret': api_secret
                    }
                    
                    files = {'media': ('image.jpg', image_bytes, 'image/jpeg')}
                    
                    r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
                    
                    if r.status_code in [401, 403, 429]:
                        last_error = f"HTTP {r.status_code}: {r.text}"
                        logger.warning(f"Sightengine API key {api_user} failed with status {r.status_code}. Trying next key...")
                        break
                        
                    r.raise_for_status()
                    output = r.json()
                    
                    if output.get("status") == "success":
                        ai_generated_score = output.get("type", {}).get("ai_generated", 0)
                        
                        if ai_generated_score >= 0.5:
                            mark = "AI"
                            confidence = ai_generated_score * 100
                            reason = "Sightengine detected a high probability of AI generation."
                            
                            generators = output.get("type", {}).get("ai_generators", {})
                            if generators:
                                top_generator = max(generators, key=generators.get)
                                reason += f" Suspected generator: {top_generator}."
                        else:
                            mark = "NONAI"
                            confidence = (1 - ai_generated_score) * 100
                            reason = "Sightengine detected a low probability of AI generation."
                            
                        return {
                            "mark": mark,
                            "confidence": round(confidence, 2),
                            "reason": reason
                        }
                    else:
                        last_error = f"API Failure: {output}"
                        logger.warning(f"Sightengine API key {api_user} failed with response: {output}. Trying next key...")
                        break
                        
                except Exception as e:
                    last_error = str(e)
                    if attempt < max_retries:
                        sleep_time = base_time * (2 ** attempt)
                        logger.warning(f"Sightengine API error with key {api_user}: {e}. Retrying in {sleep_time}s (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(sleep_time)
                    else:
                        logger.warning(f"Sightengine API failed with key {api_user} after {max_retries} retries. Trying next key...")

        raise ValueError(f"All Sightengine API keys failed. Last error: {last_error}")

    except Exception as e:
        logger.error(f"Sightengine verification failed: {e}", exc_info=True)
        return {
            "mark": "ERROR",
            "confidence": 0,
            "reason": f"Sightengine pipeline failed: {str(e)}"
        }
