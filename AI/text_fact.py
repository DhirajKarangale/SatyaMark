import json, re
from connect import get_llm
from marks_of_truth import Marks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = get_llm("deepseek_r1")

prompt_template = """
You are a factual verification assistant.

Your task is to determine whether the following statement is **factually correct** or **incorrect**
based on well-established scientific, historical, or public information.

If the statement cannot be verified (for example, it refers to future, local, or private data),
classify it as **NotFound**.

Additionally, provide your **confidence (0–100)** in how sure you are that your mark is accurate.

Respond strictly in this JSON format:
{{
  "mark": "Correct" or "Incorrect" or "NotFound",
  "reason": "<short factual reason>",
  "accuracy": <integer between 0 and 100>
}}

Statement: "{text}"

Do not include chain-of-thought, reasoning tags, or any text outside JSON.
"""

prompt = ChatPromptTemplate.from_template(prompt_template)
output_parser = StrOutputParser()


def _invoke_chain(text: str):
    """Normalizes LangChain/HuggingFace output into a plain string."""
    try:
        formatted = {"text": text}
        response = (prompt | llm | output_parser).invoke(formatted)
        if isinstance(response, dict) and "text" in response:
            return response["text"]
        if hasattr(response, "content"):
            return response.content
        return str(response)
    except Exception as e:
        print(f"[DEBUG] invoke error: {e}")
        return ""


def check_fact(text: str):
    raw_response = _invoke_chain(text).strip()
    raw_response = re.sub(
        r"<THINK>.*?</THINK>", "", raw_response, flags=re.DOTALL
    ).strip()

    json_match = re.search(r"\{[\s\S]*?\}", raw_response)
    mark_value, reason, accuracy = "", "", 0

    if json_match:
        json_str = json_match.group(0)
        try:
            parsed = json.loads(json_str)
            mark_value = parsed.get("mark", "").strip().lower()
            reason = parsed.get("reason", "").strip()
            accuracy = int(parsed.get("accuracy", 0))
        except json.JSONDecodeError:
            m_match = re.search(r'"?mark"?\s*[:=]\s*"?(\w+)"?', json_str, re.I)
            r_match = re.search(r'"?reason"?\s*[:=]\s*"?([^"}]+)"?', json_str, re.I)
            a_match = re.search(r'"?accuracy"?\s*[:=]\s*"?(\d+)"?', json_str, re.I)
            if m_match:
                mark_value = m_match.group(1).lower()
            if r_match:
                reason = r_match.group(1).strip()
            if a_match:
                accuracy = int(a_match.group(1))
    else:
        lower = raw_response.lower()
        if "correct" in lower:
            mark_value = "correct"
        elif "incorrect" in lower:
            mark_value = "incorrect"
        else:
            mark_value = "notfound"
        accuracy = 50  

    if not isinstance(accuracy, int):
        accuracy = 0
    accuracy = max(0, min(accuracy, 100))

    if mark_value == "correct":
        mark = Marks.CORRECT
    elif mark_value == "incorrect":
        mark = Marks.INCORRECT
    else:
        mark = Marks.NOTFOUND

    return {
        "mark": mark,
        "reason": reason,
        "accuracy": accuracy,
    }
