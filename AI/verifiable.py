# verifiable.py
import re
import json
import ast
from html import unescape
from typing import Any, List, Optional, Tuple
from text_summarize import summarize_text
from connect import get_llm
from marks_of_truth import Marks

# Preferred LLM order (will try to get_llm(name) in this order)
_PREFERRED_MODELS = [  "deepseek_r1","qwen2_5", "hermes", "llama3"]

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

def _build_article_from_summarized_web(new_obj: List[dict]) -> str:
    """
    Build a single ARTICLE string from a list of {"url", "data"} where
    'data' is already summarized. Each source is clearly separated and
    carries its URL so the LLM can identify which source it used.
    """
    parts = []
    for idx, item in enumerate(new_obj, start=1):
        url = (item.get("url") or "").strip()
        data = (item.get("data") or "").strip()
        if not data:
            continue

        header = f"SOURCE {idx}"
        if url:
            header += f"\nURL: {url}"

        parts.append(f"{header}\nCONTENT:\n{data}")
    return "\n\n---\n\n".join(parts)



def _clean_input_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?:\/\/\S+", " ", text)  # OK for overlap; NOT used for prompt
    text = re.sub(r"\s+", " ", text).strip()
    return text



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
- reason: a single short sentence explaining why you chose this verdict
- supporting: list of short evidence snippets from ARTICLE that support parts of SUMMARY
- contradicting: list of short evidence snippets that directly contradict parts of SUMMARY
- unmatched: list of clauses/phrases from SUMMARY that are not found in ARTICLE
- confidence: integer 0-100
- url: string, the single URL of the source in ARTICLE that is MOST relevant to your verdict.
        It MUST be exactly one of the URLs in this list: {url_options}
- notes: optional short debugging note

SUMMARY:
\"\"\"{summary}\"\"\"

ARTICLE (multiple sources, each has URL and CONTENT):
\"\"\"{article}\"\"\"

INSTRUCTIONS:
- Only compare facts present in SUMMARY to ARTICLE. Do NOT add new facts.
- SUPPORTED = all claims present & consistent.
- PARTIAL = some claims present, some missing.
- CONTRADICTED = article contains contradictory facts.
- NOT_FOUND = none of the claims found.
- Provide at most 2 supporting and 2 contradicting snippets.
- The 'url' field must exactly match one of the URLs from {url_options}. Do not add any other text.
- Output must be JSON only.
- The 'reason' must be a concise, natural language explanation of why the verdict is SUPPORTED, CONTRADICTED, PARTIAL, or NOT_FOUND.
- Do not include labels like "Supports:" or "Contradicts:" in 'reason'.
"""



# ------------------ Main function (returns same format as fact_check.check_fact) ------------------


def verify_summary_against_web(
    web_content: Any,
    summary: str,
    prefer_models: List[str] = None,
):
    # 1) Summarize in-place (if needed)
    if isinstance(web_content, list):
        #will create this function
        # new_obj = summarize_web_content_in_place(web_content)
        
        new_obj=web_content
        print(f"new input {new_obj}")
    else:
        new_obj = web_content

    # 2) Collect URL list for the prompt
    url_list = []
    if isinstance(new_obj, list):
        for item in new_obj:
            u = (item.get("url") or "").strip()
            if u:
                url_list.append(u)

    url_list = list(dict.fromkeys(url_list))   # remove duplicates
    url_options_str = json.dumps(url_list)

    # 3) Build RAW ARTICLE string (un-cleaned for LLM)
    article_raw = _build_article_from_summarized_web(new_obj)

    # 4) Clean versions only for overlap heuristic
    article_clean = _clean_input_text(article_raw)
    summary_clean = _clean_input_text(summary)

    # 5) Truncate RAW article for model context
    article_truncated = article_raw
    trunc_note = ""
    if len(article_raw) > _MAX_CHARS_FOR_PROMPT:
        head = article_raw[: _MAX_CHARS_FOR_PROMPT // 2]
        tail = article_raw[-(_MAX_CHARS_FOR_PROMPT // 2):]
        article_truncated = head + "\n\n...TRUNCATED MIDDLE...\n\n" + tail
        trunc_note = " (article truncated for model context)"

    # 6) Choose LLM
    llm, model_name = _choose_llm(prefer_models)

    # 7) Overlap score
    overlap = _overlap_score(summary_clean, article_clean)

    # 8) Build prompt
    prompt = _VERIFICATION_PROMPT.format(
        summary=summary_clean,
        article=article_truncated,
        url_options=url_options_str
    )

    # 9) Invoke model
    try:
        raw_out = _call_llm_safe(llm, prompt)
    except Exception:
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
        return {"mark": mark, "reason": reason, "accuracy": accuracy, "url": None}

    # 10) Parse JSON
    parsed = None
    try:
        parsed = json.loads(raw_out)
    except Exception:
        for cand in _find_json_candidates(raw_out):
            parsed = _safe_parse_json(cand)
            if parsed:
                break

    verdict = None
    supporting = []
    contradicting = []
    unmatched = []
    confidence = 0
    notes = ""
    selected_url = None

    if parsed and isinstance(parsed, dict):
        verdict = str(parsed.get("verdict", "")).upper() if parsed.get("verdict") else None
        reason = (parsed.get("reason") or "").strip()
        supporting = parsed.get("supporting") or parsed.get("supports") or []
        contradicting = parsed.get("contradicting") or parsed.get("contradicts") or []
        unmatched = parsed.get("unmatched") or parsed.get("missing") or []
        confidence = parsed.get("confidence") or parsed.get("accuracy") or parsed.get("score") or 0
        notes = parsed.get("notes") or ""
        raw_url = (parsed.get("url") or "").strip()

        # Validate that URL matches real sources
        if raw_url in url_list:
            selected_url = raw_url
        else:
            for u in url_list:
                if u in raw_url:
                    selected_url = u
                    break
    else:
        low = raw_out.lower()
        if "supported" in low:
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

    # sanitize confidence
    try:
        confidence = int(confidence)
    except Exception:
        confidence = int(max(0, min(100, round(overlap * 100))))

    verdict_map = {
        "SUPPORTED": Marks.CORRECT,
        "CONTRADICTED": Marks.INCORRECT,
        "PARTIAL": Marks.INSUFFICIENT,
        "NOT_FOUND": Marks.INSUFFICIENT,
    }

    mark = verdict_map.get(verdict, Marks.INSUFFICIENT)

    try:
        confidence = int(confidence)
    except Exception:
        confidence = 0
    confidence = max(0, min(100, confidence))

    if mark in (Marks.CORRECT, Marks.INCORRECT):
        # For clear verdicts, accuracy is directly how confident the model is
        accuracy = confidence if confidence > 0 else 50
    else:
        # For INSUFFICIENT (PARTIAL / NOT_FOUND), we inherently have lower certainty.
        # Use confidence but cap it so it never looks "very sure".
        base = confidence if confidence > 0 else 50
        accuracy = min(base, 70)

    # If model did not provide a reason or it's empty, fall back to a simple default
    if not reason:
        if mark == Marks.CORRECT:
            reason = "The summary is supported by the information in the sources."
        elif mark == Marks.INCORRECT:
            reason = "The summary contradicts the information in the sources."
        else:
            reason = "The sources do not provide enough information to clearly verify the summary."

    
    return {
        "mark": mark,
        "reason": reason,
        "accuracy": accuracy,
        "url": selected_url,
    }
