import re
from cleaner import clean_raw_social_text
from prompts import get_normalization_prompt
from text.utils.huggingface import invoke

NORMALIZATION_MODELS = ["qwen2_5", "llama3", "hermes"]
SUMMARIZATION_MODELS = ["bart_large_cnn", "mistral"]


def semantic_normalize(text: str) -> str:
    if not text:
        return ""
    prompt = get_normalization_prompt(text)
    try:
        result = invoke(NORMALIZATION_MODELS, prompt, parse_as_json=False)
        return result.strip() if result else text
    except Exception as e:
        print(f"Normalization failed: {e}")
        return text


def summarize_text(text: str) -> str:
    if not text:
        return ""

    try:
        prompt = f"Summarize the following text in 1 or 2 objective sentences: {text}"

        result = invoke(SUMMARIZATION_MODELS, prompt, parse_as_json=False)
        if not result:
            return text

        result = re.sub(
            r"^(summary|compressed summary|here is the summary|output):\s*",
            "",
            result,
            flags=re.IGNORECASE,
        )

        sentences = re.split(r"(?<=[.!?])\s+", result)
        if len(sentences) > 2:
            result = " ".join(sentences[:2]).strip()

        return result
    except Exception as e:
        print(f"Summarization failed: {e}")
        return text.strip()


def process_social_text_job(raw_input: str) -> str:
    cleaned_text = clean_raw_social_text(raw_input)
    if not cleaned_text:
        return ""

    normalized_text = semantic_normalize(cleaned_text)

    if not normalized_text or normalized_text == cleaned_text:
        return "" if not normalized_text else normalized_text

    # if len(normalized_text.split()) < 25:
    #     return normalized_text

    final_summary = summarize_text(normalized_text)

    return final_summary



# print("\n\nSum: ", process_social_text_job("@om416|#|17/Aug/2025|#| I like mango show more...|#| 132likes |#| comments 23 |#| Om"))
print("\n\nSum: ", process_social_text_job("Wealth Watcher |#| @WealthWatcherCo |#| In the grand tapestry of human innovation, renewable energy stands as a beacon of sustainable progress."))
