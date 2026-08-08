import logging
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_api_keys():
    keys_env = os.getenv("TRUTHSCAN_API_KEY", "")
    keys = [k.strip() for k in keys_env.split(",") if k.strip()]
    if not keys:
        keys = ["ts_live_v2_xx6I573dqATZhErvLYXmajkYtNaPz9DeSQTnpR0_jjn1ED3UMwE-e8374l49BkpO8FrpFxJJiynNQ2ZrRZDtDrFakks_MMBVEhnxMsRX2FCrqG0shhJgPQdkhOmKDhirAlbe0Pl_5812b2"]
    return keys

def verify(img):
    try:
        image_bytes = img.get("bytes")
        if not image_bytes:
            raise ValueError("No image bytes provided.")

        api_keys = get_api_keys()
        max_retries = int(os.getenv("EXPONENTIAL_BACKOFF_MAX_RETRIES", "3"))
        base_time = int(os.getenv("EXPONENTIAL_BACKOFF_BASE_TIME", "2"))
        
        last_error = None

        for API_KEY in api_keys:
            for attempt in range(max_retries + 1):
                try:
                    headers = {"apikey": API_KEY}
                    res = requests.get("https://detect-image.truthscan.com/get-presigned-url?file_name=upload.jpg", headers=headers)
                    
                    if res.status_code in [401, 403, 429]:
                        last_error = f"HTTP {res.status_code}: {res.text}"
                        logger.warning(f"TruthScan API key {API_KEY} failed with status {res.status_code}. Trying next key...")
                        break
                        
                    res.raise_for_status()
                    data = res.json()
                    
                    upload_url = data.get("presigned_url") or data.get("url")
                    file_path = data.get("file_path")
                    
                    if not upload_url or not file_path:
                        raise ValueError(f"Failed to get presigned URL or file_path. Response: {data}")
                        
                    put_headers = {"Content-Type": "image/jpeg", "x-amz-acl": "private"}
                    upload_res = requests.put(upload_url, data=image_bytes, headers=put_headers)
                    upload_res.raise_for_status()
                    
                    url_payload = f"https://ai-image-detector-prod.nyc3.digitaloceanspaces.com/{file_path}"
                    detect_payload = {
                        "key": API_KEY,
                        "url": url_payload
                    }
                    detect_res = requests.post("https://detect-image.truthscan.com/detect", json=detect_payload)
                    
                    if detect_res.status_code in [401, 403, 429]:
                        last_error = f"HTTP {detect_res.status_code}: {detect_res.text}"
                        logger.warning(f"TruthScan API key {API_KEY} failed at /detect with status {detect_res.status_code}. Trying next key...")
                        break
                        
                    detect_res.raise_for_status()
                    detect_data = detect_res.json()
                    
                    doc_id = detect_data.get("id")
                    if not doc_id:
                        raise ValueError(f"No document ID returned from /detect: {detect_data}")
                        
                    poll_max_retries = 30
                    polling_failed_due_to_auth = False
                    
                    for _ in range(poll_max_retries):
                        query_res = requests.post("https://detect-image.truthscan.com/query", json={"id": doc_id})
                        
                        if query_res.status_code in [401, 403, 429]:
                            last_error = f"HTTP {query_res.status_code}: {query_res.text}"
                            logger.warning(f"TruthScan API key {API_KEY} failed at /query with status {query_res.status_code}. Trying next key...")
                            polling_failed_due_to_auth = True
                            break
                            
                        query_res.raise_for_status()
                        query_data = query_res.json()
                        
                        if query_data.get("status") == "done":
                            ai_score = query_data.get("result", 0)
                            
                            confidence = ai_score if ai_score > 1 else ai_score * 100
                            
                            details = query_data.get("result_details", {})
                            final_result = details.get("final_result", "")
                            
                            if "AI" in str(final_result).upper() or confidence >= 50:
                                mark = "AI"
                            else:
                                mark = "NONAI"
                                confidence = 100 - confidence
                                
                            reason = "TruthScan detected " + ("high" if mark == "AI" else "low") + " probability of AI generation."
                            
                            return {
                                "mark": mark,
                                "confidence": round(confidence, 2),
                                "reason": reason
                            }
                        
                        time.sleep(2)
                    
                    if polling_failed_due_to_auth:
                        break
                        
                    raise ValueError("Timeout waiting for TruthScan detection.")

                except Exception as e:
                    last_error = str(e)
                    if attempt < max_retries:
                        sleep_time = base_time * (2 ** attempt)
                        logger.warning(f"TruthScan API error with key {API_KEY}: {e}. Retrying in {sleep_time}s (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(sleep_time)
                    else:
                        logger.warning(f"TruthScan API failed with key {API_KEY} after {max_retries} retries. Trying next key...")

        raise ValueError(f"All TruthScan API keys failed. Last error: {last_error}")

    except Exception as e:
        logger.error(f"TruthScan verification failed: {e}", exc_info=True)
        return {
            "mark": "ERROR",
            "confidence": 0,
            "reason": f"TruthScan pipeline failed: {str(e)}"
        }
