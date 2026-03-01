from text.utils.huggingface import invoke

MODELS = ["deepseek_r1", "deepseek_v3", "qwen2_5", "deepseek_r1_distill_llama_8b"]

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

TEMPORAL SAFETY RULE (MANDATORY):

If the statement involves:
- Future events
- Scheduled matches, announcements, or bookings
- Current status of titles, leadership, rosters, or organizations
- Anything that could change after your knowledge cutoff

You MUST treat the claim as "Insufficient" unless the fact is
historically fixed and universally known.

DO NOT assume your internal knowledge is current.
DO NOT use outdated status as evidence of incorrectness.

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
        data = invoke(MODELS, prompt, parse_as_json=True)
        
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