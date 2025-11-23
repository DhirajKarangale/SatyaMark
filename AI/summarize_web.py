# web_content_summarizer.py

from typing import Any, Dict, List, Optional

from connect import get_llm  # same module you use in verifiable.py

_PREFERRED_MODELS = ["deepseek_r1", "qwen2_5", "hermes", "llama3"]


def _choose_llm_for_summarization(preferred: Optional[List[str]] = None):
    """
    Simple LLM chooser for summarization, same idea as in verifiable.py.
    """
    pref = preferred or _PREFERRED_MODELS
    last_exc = None
    for name in pref:
        try:
            llm = get_llm(name)
            if (
                hasattr(llm, "invoke")
                or callable(llm)
                or hasattr(llm, "generate")
                or hasattr(llm, "create")
            ):
                return llm, name
        except Exception as e:
            last_exc = e
            continue

    # fallback attempts
    for fallback_name in ("deepseek_r1", "llama3"):
        try:
            return get_llm(fallback_name), fallback_name
        except Exception as e:
            last_exc = e

    raise RuntimeError(f"No suitable LLM available for summarization (last error: {last_exc})")


def _strip_think_block(s: str) -> str:
    """Remove any <think>...</think> block from model output."""
    if not s:
        return s
    import re as _re
    return _re.sub(r"<think>.*?</think>\s*", "", s, flags=_re.DOTALL | _re.IGNORECASE)


def _normalize_llm_output(resp: Any) -> str:
    """
    Normalize different LLM return types to a clean string (and strip <think> blocks).
    """
    if resp is None:
        return ""
    if isinstance(resp, str):
        return _strip_think_block(resp.strip())
    if hasattr(resp, "content"):
        try:
            return _strip_think_block((resp.content or "").strip())
        except Exception:
            pass
    if isinstance(resp, dict):
        return _strip_think_block((resp.get("text") or resp.get("content") or "").strip())
    try:
        if hasattr(resp, "generations"):
            gens = getattr(resp, "generations")
            if isinstance(gens, (list, tuple)) and gens:
                first = gens[0]
                if isinstance(first, (list, tuple)):
                    first = first[0]
                if hasattr(first, "text"):
                    return _strip_think_block(str(first.text).strip())
                if hasattr(first, "content"):
                    return _strip_think_block(str(first.content).strip())
        if hasattr(resp, "choices"):
            choices = getattr(resp, "choices")
            if isinstance(choices, (list, tuple)) and choices:
                c0 = choices[0]
                if isinstance(c0, dict) and "text" in c0:
                    return _strip_think_block(str(c0["text"]).strip())
                if hasattr(c0, "text"):
                    return _strip_think_block(str(c0.text).strip())
    except Exception:
        pass
    return _strip_think_block(str(resp).strip())


def _call_llm_safe(llm, prompt_text: str) -> str:
    """
    Minimal version of robust LLM caller, reused for summarization.
    """
    last_exc = None

    def _norm(resp: Any) -> str:
        return _normalize_llm_output(resp)

    # 1) try .invoke(string)
    try:
        if hasattr(llm, "invoke"):
            out = llm.invoke(prompt_text)
            return _norm(out)
    except Exception as e:
        last_exc = e

    # 2) try callable
    try:
        if callable(llm):
            out = llm(prompt_text)
            return _norm(out)
    except Exception as e:
        last_exc = e

    # 3) try .generate
    try:
        if hasattr(llm, "generate"):
            try:
                out = llm.generate(prompt_text)
            except Exception:
                out = llm.generate([prompt_text])
            return _norm(out)
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
                return _norm(out)
    except Exception as e:
        last_exc = e

    raise RuntimeError(f"All LLM invocation attempts for summarization failed. Last error: {last_exc}")


_SUMMARIZE_PROMPT = """You are a careful assistant that summarizes news and articles.

Your task:
- Read the ARTICLE.
- Focus primarily on information that is relevant to the given SUMMARY/CLAIM.
- Produce a concise summary (3–5 sentences) highlighting the most relevant facts.
- If the ARTICLE is unrelated to the SUMMARY/CLAIM, just summarize the main facts of the ARTICLE.

Return ONLY the summary text (no JSON, no extra explanation).

SUMMARY/CLAIM:
\"\"\"{summary}\"\"\"

ARTICLE:
\"\"\"{article}\"\"\"
"""


def summarize_web_content_in_place(
    web_content: List[Dict[str, Any]],
    summary: str,
    max_chars_per_article: int = 8000,
    prefer_models: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    For each object in web_content (expects {"url", "data"}), replace 'data'
    with a summary produced by an LLM, focused on the given `summary` text.

    This mutates `web_content` in place and also returns it.
    """
    if not isinstance(web_content, list):
        return web_content

    llm, model_name = _choose_llm_for_summarization(prefer_models)
    summary_text = (summary or "").strip()

    for item in web_content:
        original = (item.get("data") or "").strip()
        if not original:
            # nothing to summarize
            continue

        article_for_prompt = original
        if max_chars_per_article and len(article_for_prompt) > max_chars_per_article:
            # simple truncation to keep prompts reasonable
            head = article_for_prompt[: max_chars_per_article // 2]
            tail = article_for_prompt[-(max_chars_per_article // 2):]
            article_for_prompt = head + "\n\n...TRUNCATED MIDDLE...\n\n" + tail

        prompt = _SUMMARIZE_PROMPT.format(
            summary=summary_text,
            article=article_for_prompt,
        )

        try:
            summary_out = _call_llm_safe(llm, prompt)
        except Exception:
            # if summarization fails, keep original text
            summary_out = original

        item["data"] = (summary_out or original).strip()

    return web_content
