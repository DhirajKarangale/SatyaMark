import re
import json
from utils.huggingface import invoke_llm

TRANSLATION_MODELS = ["llama3", "qwen2_5", "mistral", "gemma_7b"]

def translate_forensics(mark, confidence, ai_score, real_score, all_reasons, raw_data):
    """
    Feeds the ENTIRE forensic payload to the LLM to generate a highly accurate, 
    context-aware, human-friendly explanation.
    """
    if not all_reasons:
        return "The image appears natural, with no signs of digital alteration or AI generation."

    data_dump = json.dumps(raw_data, indent=2)[:3000] # Cap it so we don't blow up token limits

    technical_reasons = "\n- ".join(all_reasons)

    prompt = f"""
    You are an expert digital forensics investigator. Your job is to explain an image analysis result to a non-technical client.

    [ANALYSIS RESULTS]
    Final Verdict: {mark} (AI means AI-generated/tampered. NONAI means a real photograph).
    Confidence: {confidence}%
    Score Breakdown: {ai_score} points for AI, {real_score} points for Real.

    [TRIGGERED FORENSIC FLAGS]
    - {technical_reasons}

    [RAW TELEMETRY DATA (For Context)]
    {data_dump}

    [INSTRUCTIONS - CRITICAL]
    Write a short, easily readable paragraph (3-4 sentences) explaining WHY the system reached this conclusion.
    1. Be entirely accurate to the data, but DO NOT use complex jargon. Translate the math into plain English.
        - Bad: "Latent kurtosis is 387 and chromatic aberration shift is -0.07."
        - Good: "The image contains natural camera sensor static and real physical lens distortion, which AI cannot fake."
    2. Weigh the evidence. If it's mostly real but has one AI flag, explain that it might be a real photo with heavy Photoshop editing.
    3. Be confident but professional. 
    4. Start directly with the explanation. DO NOT use prefixes like "Here is the explanation:" or "Explanation:".
    """

    try:
        result = invoke_llm(TRANSLATION_MODELS, prompt, parse_as_json=False)
        
        if not result:
            return ", ".join(all_reasons[:3]) 

        cleaned_result = re.sub(r"^(explanation|summary|output|translate|here is):\s*", "", result, flags=re.IGNORECASE).strip()
        
        return cleaned_result

    except Exception as e:
        print(f"Translation LLM failed: {e}")
        return ", ".join(all_reasons[:3]) 