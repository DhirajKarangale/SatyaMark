from utils.huggingface import invoke_llm

MODELS = ["deepseek_v3", "llama3_3_70b", "qwen2_5_72b", "deepseek_r1", "veritas_8b_fact_checker"]

PROMPT_TEMPLATE = """
You are a factual verification assistant.

You do NOT have access to the internet, news, or private data.
Use ONLY your internal general knowledge.

Task:
Classify the statement as:
- Correct
- Incorrect
- Insufficient

Rules:
- Do NOT guess.
- If unsure, choose Insufficient.
- Insufficient is valid.

EDGE CASE RULES (MANDATORY):

1. TEMPORAL SAFETY: 
   If the statement involves future events, scheduled matches, current leadership, or anything that could change after your knowledge cutoff, you MUST treat the claim as "Insufficient". DO NOT use outdated status as evidence of incorrectness.

2. PRECISION RULE:
   If a claim relies on hyper-specific data (e.g., exact statistics, highly specific dates, exact attendee numbers) and you do not have that exact number perfectly memorized, you MUST mark it "Insufficient". Do not guess that it is "Incorrect" just because the number looks unfamiliar.

3. AMBIGUITY RULE:
   If a claim is technically true but highly misleading without context, or relies on missing conditions (e.g., "Water boils at 100°C" is missing "at sea level"), or is too broad (e.g., "The US has the highest taxes"), you MUST mark it "Insufficient".

4. MYTH-BUSTING RULE:
   Be highly skeptical of common internet myths, pseudoscientific claims, and widely repeated falsehoods (e.g., "Humans only use 10% of their brains", "Chemtrails are real"). Mark them definitively as "Incorrect".

5. SUBJECTIVITY RULE:
   If the statement contains subjective opinions or value judgments (e.g., "The Matrix is the best movie") that slipped past the verifyability check, you MUST mark it "Insufficient".

Return a JSON object with:
mark, confidence (0-100), and a VERY DETAILED reason.

Statement:
{text}
"""

def fact_check(text: str) -> dict:
    if not text or not text.strip():
        return {
            "mark": "Insufficient",
            "confidence": 0,
            "reason": "No valid statement was provided for fact checking.",
        }

    try:
        prompt = PROMPT_TEMPLATE.format(text=text)
        data = invoke_llm(MODELS, prompt, parse_as_json=True)
        
        mark = data.get("mark", "").strip()
        confidence = max(0, min(int(data.get("confidence", 0)), 100))
        reason = data.get("reason", "").strip()

        if mark not in {"Correct", "Incorrect", "Insufficient"}:
            mark = "Insufficient"
        
        if not reason:
            reason = "Reasoning was not provided by the model."

        return {
            "mark": mark,
            "confidence": confidence,
            "reason": reason,
        }

    except Exception as e:
        return {
            "mark": "Insufficient",
            "confidence": 0,
            "reason": (
                f"The language model pipeline failed to return a reliably structured factual "
                f"analysis. Error: {str(e)}. To avoid guessing, the claim is marked "
                f"as Insufficient."
            ),
        }