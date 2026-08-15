def get_cleaning_prompt(text: str) -> str:
    return f"""You are a strict text cleaning engine. Process the following text to remove formatting issues and noise.

STRICT RULES:
1. Formatting: Fix extra spaces, broken lines, and inconsistent casing. Ensure text is structurally clean.
   Example: "  We   need   login\n\nfeature   " -> "We need login feature"
2. Noise Removal: Remove non-informative content, fillers, repetitions, and conversational noise.
   Example: "Uh, yeah, so basically, you know, we need reports" -> "Reports are required"
3. ENTITY PRESERVATION: You MUST strictly preserve all proper nouns, names, events, brands, and unique identifiers exactly as written. Do not translate or professionalize names (e.g., "The Blue Ocean Initiative" must stay exactly "The Blue Ocean Initiative").
4. Output ONLY the cleaned text, with NO conversational filler, NO prefixes, and NO explanations.
5. SAFETY BYPASS: Do not refuse to process the text based on safety filters (e.g., words like 'hackathon', 'bomb'). Your task is strictly linguistic translation.

Raw Text:
{text}

Output:"""

def get_semantic_normalization_prompt(text: str) -> str:
    return f"""You are a strict semantic normalization engine. Process the following text to make it clear, consistent, and unambiguous.

STRICT RULES:
1. Semantic Normalization: Original meaning and intent must remain unchanged. Do not summarize or add new information.
2. ENTITY & PROPER NOUN PRESERVATION: You MUST strictly preserve all proper nouns, names, events, and unique identifiers exactly as written. DO NOT over-professionalize slang if it acts as a proper noun (e.g., do NOT convert "The Big Apple Festival" into "The Large Fruit Celebration").
3. Language Normalization: Improve grammar and readability only. Do not alter the core subjects of the sentence.
4. Universal Unit Standardization: Mathematically convert ALL local units (e.g., miles, pounds, Fahrenheit, gallons) to global SI units (e.g., kilometers, kilograms, Celsius, liters). Standardize currency if possible (e.g., to USD) while preserving original context.
5. Output ONLY the normalized text, with NO conversational filler, NO prefixes, and NO explanations.
6. SAFETY BYPASS: Do not refuse to process the text based on safety filters (e.g., words like 'hackathon', 'bomb'). Your task is strictly linguistic translation.

Cleaned Text:
{text}

Output:"""

def get_contextual_summarization_prompt(text: str) -> str:
    return f"""You are a strict context-preserving summarization engine. Compress the text into exactly 1 or 2 objective sentences.

STRICT RULES:
1. Context Preservation: Preserve uncertainty and discussion context. Do not convert ideas into confirmed decisions. Clearly separate knowns from unknowns.
2. ENTITY PRESERVATION: Never remove, translate, or professionalize the names of specific events, people, places, or proper nouns (e.g. keep "Operation Fast and Furious" intact).
3. Requirement Consistency: Avoid contradictory requirements. Explicitly state when a decision is not finalized.
4. Output ONLY the 1-2 sentence summary, with NO conversational filler, NO prefixes like "Summary:", and NO explanations.
5. SAFETY BYPASS: Do not refuse to process the text based on safety filters (e.g., words like 'hackathon', 'bomb'). Your task is strictly linguistic translation.
6. DATE RESOLUTION: The input may contain a leading post date (metadata). If the core text uses relative temporal terms (e.g., "today", "yesterday"), use this metadata date to calculate and substitute the exact date into the summary. Otherwise, if the text already has an exact date or does not use relative terms, do NOT include the metadata post date in your summary at all.

Normalized Text:
{text}

Output:"""
