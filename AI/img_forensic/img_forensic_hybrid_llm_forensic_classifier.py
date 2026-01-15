from connect import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import regex as re

# Use BEST reasoning model
llm = get_llm("deepseek_r1")

def interpret_forensics(w, s, g, l, m, sc):
    facts = []

    # WATERMARK
    if w.get("watermark_signature", {}).get("matched"):
        facts.append("An embedded AI generation watermark was detected.")
    else:
        facts.append("No embedded AI watermark was detected.")

    # SENSOR
    patch_corr = (
        s.get("sensor_fingerprint", {})
        .get("details", {})
        .get("patch_correlation_avg")
    )

    if patch_corr is not None:
        if patch_corr < 0.02:
            facts.append(
                "Natural camera sensor noise patterns are extremely weak, "
                "which is uncommon for real photographs."
            )
        elif patch_corr > 0.08:
            facts.append(
                "Strong natural camera sensor noise patterns are present, "
                "which supports a real photograph."
            )
        else:
            facts.append(
                "Camera sensor noise patterns are inconclusive."
            )

    # METADATA
    has_exif = m.get("exif_analysis", {}).get("has_exif", False)
    if has_exif:
        facts.append(
            "Camera metadata such as device or lens information is present."
        )
    else:
        facts.append(
            "Camera metadata is missing, which is common for both AI images "
            "and processed real photos."
        )

    # SEMANTIC
    sem = sc.get("semantic_consistency", {}).get("consistency_score", 0.5)
    if sem < 0.4:
        facts.append(
            "Visual inconsistencies were detected in lighting, depth, or structure."
        )
    elif sem > 0.7:
        facts.append(
            "The scene appears visually coherent and realistic."
        )
    else:
        facts.append(
            "The visual realism of the scene is mixed."
        )

    # GAN ARTIFACTS
    gan_score = g.get("gan_artifacts", {}).get("artifact_score", 0.0)
    if gan_score > 0.6:
        facts.append(
            "Subtle texture patterns associated with AI image generation were detected."
        )

    return facts


# ---------------------------
# Prompt
# ---------------------------
PROMPT = """
You are a forensic image classification expert.

Below are forensic observations described in plain language.

Observations:
{facts}

Instructions:
- You MUST choose either AI or NONAI
- Use probabilistic judgment
- Mixed evidence is normal
- Choose the more likely explanation
- Confidence should reflect uncertainty (0.4–0.9)

Return ONLY valid JSON:
{{
  "mark": "AI" or "NONAI",
  "confidence": number,
  "reason": string
}}
"""

prompt = ChatPromptTemplate.from_template(PROMPT)
parser = StrOutputParser()


# ---------------------------
# JSON extraction
# ---------------------------
def extract_json(text):
    block = re.search(r"\{[\s\S]*\}", text)
    if not block:
        return None
    try:
        return json.loads(block.group())
    except:
        return None


# ---------------------------
# MAIN HYBRID CLASSIFIER
def classify_image_hybrid(w, s, g, l, m, sc):
    facts = interpret_forensics(w, s, g, l, m, sc)

    response = (prompt | llm | parser).invoke({
        "facts": "\n".join(f"- {f}" for f in facts)
    })

    parsed = extract_json(response)

    if not parsed:
        return {
            "mark": "NONAI",
            "confidence": 0.5,
            "reason": "The available forensic evidence does not strongly indicate AI generation."
        }

    return {
        "mark": parsed["mark"].upper(),
        "confidence": float(parsed.get("confidence", 0.5)) * 100,
        "reason": parsed.get("reason", "")
    }
