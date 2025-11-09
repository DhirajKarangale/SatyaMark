
import os
import sys
import argparse
from textwrap import dedent
from dotenv import load_dotenv

# Optional: pip install langdetect
try:
    from langdetect import detect
except Exception:
    detect = None

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


def build_llama3_summarizer_chain(
    repo_id: str,
    provider: str,
    task: str,
    max_new_tokens: int,
    temperature: float,
    repetition_penalty: float = 1.03,
):
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        task=task,                     # usually "conversational"
        provider=provider,             # e.g., "auto"
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
        temperature=temperature,
        repetition_penalty=repetition_penalty,
        return_full_text=False,
    )

    chat = ChatHuggingFace(llm=llm)

    # >>> STRONG, REDUNDANT ENGLISH-ONLY INSTRUCTIONS + FEW-SHOT <<<
    system_msg = dedent("""\
        You are a professional summarizer.

        CRITICAL REQUIREMENTS:
        - ALWAYS respond in ENGLISH ONLY, regardless of the input language.
        - If the input is not in English, first infer/translate the important content into English,
          then write the summary in plain, simple English.
        - Do NOT include any non-English words in the output (no code-switching).
        - Do NOT add new facts beyond what is provided.
        - Prefer short sentences, everyday words, and neutral tone.
        - Keep key numbers, names, and dates when relevant.

        OUTPUT FORMAT:
        1) 4–7 bullet points with the key facts.
        2) A short 2–3 sentence paragraph with the overall gist.
    """)

    # A tiny few-shot: Non-English input → English output
    fewshot_user = "Résumé (français): « Le rapport explique la baisse des ventes au T2 et propose trois actions pour le T3. »"
    fewshot_assistant = (
        "- The report analyzes lower sales in Q2.\n"
        "- It lists three actions planned for Q3 to improve results.\n"
        "- The focus is on operational fixes and marketing.\n\n"
        "Overall: The document explains why Q2 sales fell and outlines three practical steps intended to boost performance in Q3."
    )

    human_msg = "{text}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", fewshot_user),
        ("assistant", fewshot_assistant),
        ("human", human_msg),
    ])

    return prompt | chat | StrOutputParser()


def read_input_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    sys.stderr.write(
        "ERROR: Provide --text, --input-file, or pipe content via STDIN.\n"
        "Example: echo \"<your text>\" | python summarize_llama3_english.py\n"
    )
    sys.exit(2)


def looks_english(text: str) -> bool:
    # Prefer langdetect when available; fallback to a simple ASCII/latin heuristic.
    if detect:
        try:
            return detect(text) == "en"
        except Exception:
            pass
    # Heuristic: if most characters are basic Latin, assume English.
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return True
    ascii_letters = [c for c in letters if ord(c) < 128]
    return (len(ascii_letters) / max(1, len(letters))) > 0.92


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Multilingual → Plain English summarizer (Llama 3 via Hugging Face, LangChain)."
    )
    parser.add_argument("--text", help="Raw input text to summarize.")
    parser.add_argument("--input-file", help="Path to a UTF-8 text file to summarize.")
    parser.add_argument("--repo-id",
                        default=os.getenv("HF_REPO_ID", "meta-llama/Meta-Llama-3-8B-Instruct"),
                        help="Hugging Face model repo id (default: %(default)s)")
    parser.add_argument("--provider",
                        default=os.getenv("HF_PROVIDER", "auto"),
                        help="Provider hint for HuggingFaceEndpoint (default: %(default)s)")
    parser.add_argument("--task",
                        choices=["conversational", "text-generation"],
                        default=os.getenv("HF_TASK", "conversational"),
                        help="HF task (chat/instruct models usually prefer 'conversational').")
    parser.add_argument("--max-new-tokens", type=int, default=int(os.getenv("MAX_NEW_TOKENS", "512")))
    parser.add_argument("--temperature", type=float, default=float(os.getenv("TEMPERATURE", "0.2")))
    parser.add_argument("--repetition-penalty", type=float, default=float(os.getenv("REPETITION_PENALTY", "1.03")))
    parser.add_argument("--enforce-english", action="store_true",
                        help="If set, auto-retry once with a stronger prompt if output isn't English.")
    args = parser.parse_args()

    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        sys.stderr.write(
            "ERROR: HUGGINGFACEHUB_API_TOKEN not found.\n"
            "Put it in your environment or a .env file.\n"
        )
        sys.exit(1)

    text = read_input_text(args)
    chain = build_llama3_summarizer_chain(
        repo_id=args.repo_id,
        provider=args.provider,
        task=args.task,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        repetition_penalty=args.repetition_penalty,
    )

    summary = chain.invoke({"text": text})

    if args.enforce_english and not looks_english(summary):
        # One retry with a forceful instruction
        force_prompt = ChatPromptTemplate.from_messages([
            ("system", "Rewrite the following into PLAIN, SIMPLE ENGLISH ONLY. No other language."),
            ("human", "{draft}")
        ])
        # Reuse same chat model behind the scenes
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser as _Parser
        forced_chain = force_prompt | chain.bound.llm | _Parser()
        summary = forced_chain.invoke({"draft": summary})

    print(summary)


if __name__ == "__main__":
    main()
