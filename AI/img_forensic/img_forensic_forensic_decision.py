import re
import json
from connect import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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


llm = get_llm("deepseek_r1_distill_llama_8b")


prompt_template = """
You classify images as AI or NONAI using weighted forensic signals.

Keep reasoning SHORT. Do NOT internally think. Do NOT generate long text.

Weightage:
- Sensor: 0.35 (very strong)
- Metadata: 0.25 (strong)
- Semantic Consistency: 0.20 (medium)
- Manipulation: 0.10 (medium)
- Watermark: 0.07 (weak)
- GAN Artifacts: 0.03 (very weak – use minimally)

Input Summary:
W:{watermark}
S:{sensor}
G:{gan}
M:{manip}
D:{meta}
C:{semantic}

Rules:
- Weak sensor + missing EXIF + multiple inconsistencies → AI
- Strong sensor + real EXIF + stable semantics → NONAI
- GAN artifacts have VERY LOW weight — NEVER base decision mainly on them.

Return ONLY compact JSON:
{{
  "mark": "AI" or "NONAI",
  "reason": "short explanation",
  "confidence": "0-1 number"
}}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()


def _clean(response: str):
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    m = re.search(r"\{[\s\S]*\}", response)
    return m.group(0) if m else "{}"


def classify_image(
    watermark: dict, sensor: dict, gan: dict, manip: dict, meta: dict, semantic: dict
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

        response = (prompt | llm | output_parser).invoke(formatted)

        if isinstance(response, dict):
            response = response.get("text", "")

        response = _clean(response)
        parsed = json.loads(response)

        parsed["mark"] = parsed.get("mark", "").upper()
        parsed["confidence"] = float(parsed.get("confidence", 0))

        return parsed

    except Exception as e:
        return {"mark": "AI", "reason": f"LLM error: {str(e)}", "confidence": 0.5}
