# verifiable.py
import re
import json
import ast
from html import unescape
from typing import Any, List, Optional, Tuple

from connect import get_llm
from marks_of_truth import Marks

# Preferred LLM order (will try to get_llm(name) in this order)
_PREFERRED_MODELS = [ "qwen2_5", "hermes", "deepseek_r1", "llama3"]

# small stopword set for overlap checks
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "these", "those", "a", "an",
    "in", "on", "at", "to", "of", "is", "are", "was", "were", "be", "been",
    "by", "as", "it", "its", "from", "or", "but", "not", "which", "will",
    "can", "may", "has", "have", "had", "we", "i", "you", "they", "he", "she"
}

# Max chars to include from article when building the prompt (to avoid token limits)
_MAX_CHARS_FOR_PROMPT = 16000


# ------------------ Utilities ------------------

def _choose_llm(preferred: Optional[List[str]] = None):
    pref = preferred or _PREFERRED_MODELS
    last_exc = None
    for name in pref:
        try:
            llm = get_llm(name)
            if hasattr(llm, "invoke") or callable(llm) or hasattr(llm, "generate") or hasattr(llm, "create"):
                return llm, name
        except Exception as e:
            last_exc = e
            continue
    # robust fallback attempts
    for fallback_name in ("deepseek_r1", "llama3"):
        try:
            return get_llm(fallback_name), fallback_name
        except Exception as e:
            last_exc = e
    raise RuntimeError(f"No suitable LLM available (last error: {last_exc})")


def _normalize_web_content(val: Any) -> str:
    if isinstance(val, str):
        s = val.strip()
        if s and s[0] in ("{", "["):
            try:
                parsed = json.loads(s)
                val = parsed
            except Exception:
                try:
                    val = ast.literal_eval(s)
                except Exception:
                    return s
        else:
            return s
    if isinstance(val, list):
        parts = []
        urls = []
        for item in val:
            if isinstance(item, dict):
                data = item.get("data") or item.get("text") or ""
                url = item.get("url") or ""
                if isinstance(data, str) and data.strip():
                    parts.append(data.strip())
                elif url:
                    urls.append(url)
            elif isinstance(item, str) and item.strip():
                parts.append(item.strip())
        if parts:
            return "\n\n".join(parts)
        if urls:
            return "\n".join(urls)
        return ""
    if isinstance(val, dict):
        if "data" in val and isinstance(val["data"], str) and val["data"].strip():
            return val["data"].strip()
        if "text" in val and isinstance(val["text"], str) and val["text"].strip():
            return val["text"].strip()
        parts = [v.strip() for v in val.values() if isinstance(v, str) and v.strip()]
        return "\n\n".join(parts)
    return str(val) if val is not None else ""


def _clean_input_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?:\/\/\S+", " ", text)
    text = re.sub(r"[@#]\w+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _content_token_set(text: str) -> set:
    tokens = re.findall(r"\w+", text.lower())
    return {t for t in tokens if len(t) > 2 and t not in _STOPWORDS}


def _overlap_score(summary: str, source: str) -> float:
    sset = _content_token_set(summary)
    if not sset:
        return 0.0
    srcset = _content_token_set(source)
    match = sum(1 for t in sset if t in srcset)
    return match / len(sset)


def _normalize_llm_output(resp: Any) -> str:
    if resp is None:
        return ""
    if isinstance(resp, str):
        return resp.strip()
    if hasattr(resp, "content"):
        try:
            return (resp.content or "").strip()
        except Exception:
            pass
    if isinstance(resp, dict):
        return (resp.get("text") or resp.get("content") or "").strip()
    # try common nested structures
    try:
        if hasattr(resp, "generations"):
            gens = getattr(resp, "generations")
            if isinstance(gens, (list, tuple)) and gens:
                first = gens[0]
                if isinstance(first, (list, tuple)):
                    first = first[0]
                if hasattr(first, "text"):
                    return str(first.text).strip()
                if hasattr(first, "content"):
                    return str(first.content).strip()
        if hasattr(resp, "choices"):
            choices = getattr(resp, "choices")
            if isinstance(choices, (list, tuple)) and choices:
                c0 = choices[0]
                if isinstance(c0, dict) and "text" in c0:
                    return str(c0["text"]).strip()
                if hasattr(c0, "text"):
                    return str(c0.text).strip()
    except Exception:
        pass
    return str(resp).strip()


def _find_json_candidates(text: str) -> List[str]:
    candidates = []
    stack = []
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if start is None:
                start = i
            stack.append(i)
        elif ch == "}":
            if stack:
                stack.pop()
            if not stack and start is not None:
                candidates.append(text[start:i + 1])
                start = None
    if not candidates:
        candidates = [m.group(0) for m in re.finditer(r"\{[^}]*\}", text, flags=re.DOTALL)]
    return candidates


def _safe_parse_json(s: str) -> Optional[dict]:
    try:
        return json.loads(s)
    except Exception:
        s2 = s.replace("’", "'").replace("“", '"').replace("”", '"')
        s2 = re.sub(r",\s*([}\]])", r"\1", s2)
        try:
            return json.loads(s2)
        except Exception:
            kvs = re.findall(r'"?(\w+)"?\s*[:=]\s*("?[^",}]+\"?)', s)
            if kvs:
                out = {}
                for k, v in kvs:
                    v_clean = v.strip().strip('"').strip()
                    if k.lower() in ("confidence", "accuracy", "score"):
                        m = re.search(r"(\d+)", v_clean)
                        out[k] = int(m.group(1)) if m else v_clean
                    else:
                        out[k] = v_clean
                return out
    return None


def _call_llm_safe(llm, prompt_text: str, timeout_seconds: Optional[int] = None) -> str:
    """
    Robust LLM caller that tries common invocation patterns and returns a normalized string.
    Tries several invocation styles and normalizes typical return types.
    """
    last_exc = None

    def _normalize(resp: Any) -> str:
        return _normalize_llm_output(resp)

    # 1) try .invoke(string)
    try:
        if hasattr(llm, "invoke"):
            out = llm.invoke(prompt_text)
            return _normalize(out)
    except Exception as e:
        last_exc = e

    # 2) try calling llm as a callable: llm(prompt_text)
    try:
        if callable(llm):
            out = llm(prompt_text)
            return _normalize(out)
    except Exception as e:
        last_exc = e

    # 3) try .generate / .generate([prompt_text])
    try:
        if hasattr(llm, "generate"):
            try:
                out = llm.generate(prompt_text)
            except Exception:
                out = llm.generate([prompt_text])
            return _normalize(out)
    except Exception as e:
        last_exc = e

    # 4) try .create / .completion / .chat_completion
    try:
        for fn_name in ("create", "completion", "chat_completion"):
            if hasattr(llm, fn_name):
                create_fn = getattr(llm, fn_name)
                try:
                    out = create_fn(prompt=prompt_text)
                except TypeError:
                    out = create_fn(prompt=[prompt_text])
                return _normalize(out)
    except Exception as e:
        last_exc = e

    raise RuntimeError(f"All LLM invocation attempts failed. Last error: {last_exc}")


# ------------------ Prompt ------------------

_VERIFICATION_PROMPT = """You are a precise fact-verification assistant.
Return ONLY a single JSON object (no prose) with keys:
- verdict: one of ["SUPPORTED","PARTIAL","CONTRADICTED","NOT_FOUND"]
- supporting: list of short evidence snippets from ARTICLE that support parts of SUMMARY
- contradicting: list of short evidence snippets that directly contradict parts of SUMMARY
- unmatched: list of clauses/phrases from SUMMARY that are not found in ARTICLE
- confidence: integer 0-100
- notes: optional short debugging note

SUMMARY:
\"\"\"{summary}\"\"\"

ARTICLE:
\"\"\"{article}\"\"\"

INSTRUCTIONS:
- Only compare facts present in SUMMARY to ARTICLE. Do NOT add new facts.
- SUPPORTED = all claims present & consistent.
- PARTIAL = some claims present, some missing.
- CONTRADICTED = article contains contradictory facts.
- NOT_FOUND = none of the claims found.
- Provide at most 2 supporting and 2 contradicting snippets.
- Output must be JSON only.
"""


# ------------------ Main function (returns same format as fact_check.check_fact) ------------------

def verify_summary_against_web(web_content: Any, summary: str, prefer_models: List[str] = None, debug: bool = False):
    """
    Verifies whether the given summary's facts are supported by the web_content.
    Returns dict in same format as fact_check.check_fact():
        {
          "mark": Marks.<CORRECT|INCORRECT|SUBJECTIVE|INSUFFICIENT>,
          "reason": "<brief justification or evidence summary>",
          "accuracy": int(0-100)
        }
    """
    raw_text = _normalize_web_content(web_content)
    article = _clean_input_text(raw_text)
    summary_clean = _clean_input_text(summary)

    # Truncate article for prompt if very long (keep head+taiI)
    article_truncated = article
    trunc_note = ""
    if len(article) > _MAX_CHARS_FOR_PROMPT:
        head = article[: _MAX_CHARS_FOR_PROMPT // 2]
        tail = article[-(_MAX_CHARS_FOR_PROMPT // 2) :]
        article_truncated = head + "\n\n...TRUNCATED MIDDLE...\n\n" + tail
        trunc_note = " (article truncated for model context)"

    # Choose LLM
    llm, model_name = _choose_llm(prefer_models)

    overlap = _overlap_score(summary_clean, article)
    prompt = _VERIFICATION_PROMPT.format(summary=summary_clean, article=article_truncated)

    # Invoke model (robust)
    try:
        raw_out = _call_llm_safe(llm, prompt)
    except Exception as e:
        if debug:
            print(f"[DEBUG] LLM invocation failed: {e}")
        # fallback to extractive heuristic if model cannot be called
        reason = "LLM invocation failed; falling back to extractive overlap check."
        if overlap >= 0.8:
            mark = Marks.CORRECT
            accuracy = int(min(95, int(overlap * 100)))
        elif overlap >= 0.4:
            mark = Marks.INSUFFICIENT
            accuracy = int(min(75, int(overlap * 100)))
        else:
            mark = Marks.INSUFFICIENT
            accuracy = int(min(50, int(overlap * 100)))
        return {"mark": mark, "reason": reason, "accuracy": accuracy}

    if debug:
        print("[DEBUG] raw_out:", raw_out[:1000].replace("\n", " "))

    # Try extracting JSON
    parsed = None
    try:
        parsed = json.loads(raw_out)
    except Exception:
        for cand in _find_json_candidates(raw_out):
            parsed = _safe_parse_json(cand)
            if parsed:
                break

    # If parsed exists, map verdict->Marks, compute accuracy from confidence+overlap
    verdict = None
    supporting = []
    contradicting = []
    unmatched = []
    confidence = 0
    notes = ""

    if parsed and isinstance(parsed, dict):
        verdict = str(parsed.get("verdict", "")).upper() if parsed.get("verdict") else None
        supporting = parsed.get("supporting") or parsed.get("supports") or []
        contradicting = parsed.get("contradicting") or parsed.get("contradicts") or []
        unmatched = parsed.get("unmatched") or parsed.get("missing") or []
        confidence = parsed.get("confidence") or parsed.get("accuracy") or parsed.get("score") or 0
        notes = parsed.get("notes") or ""
    else:
        low = raw_out.lower()
        if "subjective" in low:
            verdict = "NOT_FOUND"
            notes = "Model labeled subjective in raw text."
            confidence = int(min(60, int(overlap * 100)))
        elif "supported" in low:
            verdict = "SUPPORTED"
            confidence = int(min(85, int(overlap * 100)))
        elif "contradict" in low:
            verdict = "CONTRADICTED"
            confidence = int(min(85, int(overlap * 100)))
        elif "partial" in low or "some" in low:
            verdict = "PARTIAL"
            confidence = int(min(80, int(overlap * 100)))
        else:
            verdict = "NOT_FOUND"
            confidence = int(min(70, int(overlap * 100)))
            notes = "Fallback parsing used."
            # include snippet for debugging
            if debug:
                notes = notes + " Raw model output (truncated): " + raw_out[:500].replace("\n", " ")

    # sanitize confidence
    try:
        confidence = int(confidence)
    except Exception:
        confidence = int(max(0, min(100, round(overlap * 100))))

    # Map verdict to Marks
    verdict_map = {
        "SUPPORTED": Marks.CORRECT,
        "CONTRADICTED": Marks.INCORRECT,
        "PARTIAL": Marks.INSUFFICIENT,
        "NOT_FOUND": Marks.INSUFFICIENT,
    }
    mark = verdict_map.get(verdict, Marks.INSUFFICIENT)

    # Build reason: prefer short summarizing evidence
    reason_parts = []
    # coerce lists if strings
    if isinstance(supporting, str):
        supporting = [supporting]
    if isinstance(contradicting, str):
        contradicting = [contradicting]
    if isinstance(unmatched, str):
        unmatched = [unmatched]

    if supporting:
        s_samples = [str(x).strip() for x in supporting[:2] if x]
        if s_samples:
            reason_parts.append("Supports: " + " | ".join(s_samples))
    if contradicting:
        c_samples = [str(x).strip() for x in contradicting[:2] if x]
        if c_samples:
            reason_parts.append("Contradicts: " + " | ".join(c_samples))
    if unmatched:
        u_samples = [str(x).strip() for x in unmatched[:3] if x]
        if u_samples:
            reason_parts.append("Unmatched claims: " + "; ".join(u_samples))

    if not reason_parts:
        if overlap >= 0.8:
            reason_parts.append("High textual overlap with article (extractive evidence).")
        elif overlap >= 0.4:
            reason_parts.append("Partial textual overlap; some claims may be missing or paraphrased.")
        else:
            reason_parts.append("No clear textual evidence found in the article.")
    if notes:
        reason_parts.append(f"Notes: {notes}")
    if trunc_note:
        reason_parts.append(trunc_note.strip())

    reason = " ".join(reason_parts).strip()

    # Derive final accuracy: combine model confidence and overlap heuristically
    accuracy = int(max(0, min(100, round(0.6 * confidence + 0.4 * overlap * 100))))

    return {"mark": mark, "reason": reason, "accuracy": accuracy}


