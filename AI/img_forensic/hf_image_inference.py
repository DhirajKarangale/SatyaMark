import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")  
HF_API_URL = "https://api-inference.huggingface.co/models/{}"


def hf_infer(model_id: str, image_bytes: bytes):
    """Universal HuggingFace image inference wrapper"""
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Accept": "application/json"
    }

    res = requests.post(
        HF_API_URL.format(model_id),
        headers=headers,
        data=image_bytes
    )

    try:
        return res.json()
    except Exception:
        return {"error": "Invalid HF response", "raw": res.text}
