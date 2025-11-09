# text_summarize.py
from connect import get_llm

def summarize_text(text: str) -> str:
    """
    Summarize any text (multilingual) into short, simple English.
    
    Args:
        text: Input text to summarize.
        
    Returns:
        Summarized text as a string.
    """
    llm = get_llm("llama3")  # Use the configured LLM

    # Prompt for multilingual → plain English summarization
    prompt = f"""
    You are a professional summarizer.
    
    CRITICAL REQUIREMENTS:
    - Always respond in English only, regardless of the input language.
    - Translate important content into English if input is not English.
    - Do not add new facts beyond what is provided.
    - Prefer short sentences, everyday words, and neutral tone.
    - Keep key numbers, names, and dates when relevant.
    
    OUTPUT FORMAT:
    1) 4–7 bullet points with key facts.
    2) A short 2–3 sentence paragraph with the overall gist.
    
    Text to summarize:
    {text}
    """

    # Get the summary from the LLM
    summary = llm.invoke(prompt)

    # Force English rewrite (always applied)
    force_prompt = f"Rewrite the following into plain, simple English only. No other language:\n{summary}"
    summary = llm.invoke(force_prompt)

    return summary
