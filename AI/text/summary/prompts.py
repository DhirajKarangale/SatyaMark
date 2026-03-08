def get_normalization_prompt(text: str) -> str:
    return f"""You are a strict text extraction engine. Process the following segmented social media text to isolate the core user message.

STRICT RULES:
1. Truncation & UI Removal (PRIORITY): Identify and delete any trailing text that indicates the message was cut off by a user interface (such as standalone words ending in ellipses indicating expanded text, or isolated action verbs). Do not leave floating ellipses.
2. Pure Extraction: Isolate only the main statement or thought. Completely ignore standalone names, isolated usernames, dates, and disconnected UI words.
3. Zero Editing (Literal Preservation): Do NOT fix typos, broken grammar, or casing of the core message. Keep the exact original phrasing (e.g., leave "America attack iran" exactly as written). 
4. Perspective Retention: Do NOT convert first-person statements to third-person.
5. Zero Hallucination: Do not add external context, guess missing details, or invent information.

Raw Text:
{text}

Return ONLY the exact extracted message without any introductions:"""


def get_summarization_prompt(text: str) -> str:
    return f"""Compress the following text into 1 or 2 sentences ONLY if it is lengthy.

STRICT RULES:
1. SHORT TEXT BYPASS (PRIORITY): If the text is short (under 30 words), you MUST return it exactly word-for-word. Do not summarize, rephrase, or fix grammar.
2. PERSPECTIVE RETENTION: Never shift the perspective. Do NOT use phrases like "The speaker expresses", "The user says", or "The text states". Keep "I" as "I". 
3. NO META-COMMENTARY: Do not add conversational filler, labels, or explain what the text means.
4. Output ONLY the final text.

Text:
{text}

Output:"""
