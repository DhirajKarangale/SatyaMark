import regex as re
import json
from connect import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# -----------------------------------------------------------
# Summarizer (kept same as your original)
# -----------------------------------------------------------
def summarize(data: dict):
    """Extract only the most meaningful numeric/boolean signals."""
    out = []
    try:
        for k, v in data.items():
            if isinstance(v, (int, float, str, bool)):
                out.append(f"{k}:{v}")
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, (int, float, str, bool)):
                        out.append(f"{k}.{k2}:{v2}")
            if len(out) > 12:
                break
        return "; ".join(out[:12])
    except:
        return "ERR"


# -----------------------------------------------------------
# JSON EXTRACTION (fixed)
# -----------------------------------------------------------
def extract_json_block(text: str):
    """
    Extract JSON from:
    - ```json fenced blocks```
    - or raw { ... } structures
    """
    if not isinstance(text, str):
        return None

    # 1) JSON inside code fences
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    # 2) raw { ... } JSON blocks (recursive)
    blocks = re.findall(r"\{(?:[^{}]|(?R))*\}", text, flags=re.DOTALL)
    if blocks:
        return blocks[-1].strip()

    return None


# -----------------------------------------------------------
# JSON FIXER (defensive)
# -----------------------------------------------------------
def fix_json_string(bad_json: str):
    """Fix common LLM formatting mistakes."""
    if not isinstance(bad_json, str):
        return ""

    s = bad_json.replace("\r", " ").replace("\n", " ").strip()

    # Remove trailing commas
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*]", "]", s)

    # Quote missing keys
    s = re.sub(r'([{,\s])([A-Za-z0-9_]+)\s*:', r'\1"\2":', s)

    # Replace single quotes with double quotes
    s = re.sub(r"'([^']*)'", r'"\1"', s)

    return s


# -----------------------------------------------------------
# JSON SAFE LOAD
# -----------------------------------------------------------
def safe_json_load(text: str):
    try:
        return json.loads(text)
    except:
        pass

    try:
        import json5
        return json5.loads(text)
    except:
        pass

    return None


# -----------------------------------------------------------
# LLM CONFIG
# -----------------------------------------------------------
llm = get_llm("deepseek_r1_distill_llama_8b")

prompt_template = """
You classify images as AI or NONAI using weighted forensic signals.

Keep reasoning VERY SHORT. NO internal thoughts. NO markdown. NO code fences.

Weightage:
- Sensor: 0.35
- Metadata: 0.25
- Semantic Consistency: 0.20
- Manipulation: 0.10
- Watermark: 0.07
- GAN Artifacts: 0.03

Input Summary:
W:{watermark}
S:{sensor}
G:{gan}
M:{manip}
D:{meta}
C:{semantic}

Rules:
- Weak sensor + missing EXIF + strong inconsistencies → AI
- Strong sensor + valid EXIF + stable semantics → NONAI
- GAN artifacts are VERY weak; do not overuse them.

RETURN STRICT JSON **ONLY ONE OBJECT**, NO BACKTICKS, NO EXTRA TEXT:

{{
  "mark": "AI" or "NONAI",
  "reason": "short reason",
  "confidence": <0-1>
}}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()


# -----------------------------------------------------------
# MAIN CLASSIFIER
# -----------------------------------------------------------
def classify_image(
    watermark: dict,
    sensor: dict,
    gan: dict,
    manip: dict,
    meta: dict,
    semantic: dict,
):

    try:
        formatted = {
            "watermark": summarize(watermark),
            "sensor": summarize(sensor),
            "gan": summarize(gan),
            "manip": summarize(manip),
            "meta": summarize(meta),
            "semantic": summarize(semantic),
        }

        print("formatted: ", formatted)

        # Get raw response from LLM
        response = (prompt | llm | output_parser).invoke(formatted)

        if isinstance(response, dict):
            response = response.get("text", "")

        print("\nraw LLM response preview:\n", response[:500], "\n")

        # 1) Extract any JSON block or fallback
        raw_json = extract_json_block(response)
        if not raw_json:
            return {"mark": "AI", "reason": "No JSON found", "confidence": 0.5}

        # 2) Fix JSON
        fixed = fix_json_string(raw_json)

        # 3) Parse JSON
        parsed = safe_json_load(fixed)

        if not parsed or not isinstance(parsed, dict):
            print("FAILED PARSING:", fixed)
            return {"mark": "AI", "reason": "Invalid JSON from LLM", "confidence": 0.5}

        # Normalize fields
        parsed["mark"] = parsed.get("mark", "").upper()

        try:
            parsed["confidence"] = float(parsed.get("confidence", 0))
        except:
            parsed["confidence"] = 0.0

        return parsed

    except Exception as e:
        return {"mark": "AI", "reason": f"LLM error: {str(e)}", "confidence": 0.5}
