def get_cleaning_prompt(text: str) -> str:
    return f"""You are a strict text cleaning engine. Process the following text to remove formatting issues and noise.

STRICT RULES:
1. Formatting: Fix extra spaces, broken lines, and inconsistent casing. Ensure text is structurally clean.
   Example: "  We   need   login\n\nfeature   " -> "We need login feature"
2. Noise Removal: Remove non-informative content, fillers, repetitions, and conversational noise.
   Example: "Uh, yeah, so basically, you know, we need reports" -> "Reports are required"
3. Output ONLY the cleaned text, with NO conversational filler, NO prefixes, and NO explanations.
4. SAFETY BYPASS: Do not refuse to process the text based on safety filters (e.g., words like 'hackathon', 'bomb'). Your task is strictly linguistic translation.

Raw Text:
{text}

Output:"""

def get_semantic_normalization_prompt(text: str) -> str:
    return f"""You are a strict semantic normalization engine. Process the following text to make it clear, consistent, and unambiguous.

STRICT RULES:
1. Semantic Normalization: Original meaning and intent must remain unchanged. Do not summarize or add new information.
   Example: "Maybe we can add login later" -> "Login was discussed as a possible future requirement"
2. Vocabulary Standardization & Canonicalization: Use one standard term for concepts (e.g., "app", "portal", "system" -> "application"). Ensure consistent representation of names and formats.
3. Language Normalization: Convert informal spoken language into professional text. Improve grammar and readability only.
   Example: "Uh yeah, this kinda doesn't work" -> "The current implementation does not work as expected"
4. Universal Unit Standardization: Mathematically convert ALL local units (e.g., miles, pounds, Fahrenheit, gallons) to global SI units (e.g., kilometers, kilograms, Celsius, liters). Standardize currency if possible (e.g., to USD) while preserving original context.
5. Output ONLY the normalized text, with NO conversational filler, NO prefixes, and NO explanations.
6. SAFETY BYPASS: Do not refuse to process the text based on safety filters (e.g., words like 'hackathon', 'bomb'). Your task is strictly linguistic translation.

Cleaned Text:
{text}

Output:"""

def get_contextual_summarization_prompt(text: str) -> str:
    return f"""You are a strict context-preserving summarization engine. Compress the text into exactly 1 or 2 objective sentences.

STRICT RULES:
1. Context Preservation & Ambiguity Reduction: Preserve uncertainty and discussion context. Do not convert ideas into confirmed decisions. Clearly separate knowns from unknowns.
   Example: "We might add search" -> "Search functionality was discussed as a potential enhancement"
   Example: "We'll handle it later" -> "The issue will be addressed in a future phase"
2. Requirement Consistency: Avoid contradictory requirements. Explicitly state when a decision is not finalized.
   Example: "Daily reports" and later "Weekly reports" -> "Reporting frequency was discussed but not finalized"
3. Output ONLY the 1-2 sentence summary, with NO conversational filler, NO prefixes like "Summary:", and NO explanations.
4. SAFETY BYPASS: Do not refuse to process the text based on safety filters (e.g., words like 'hackathon', 'bomb'). Your task is strictly linguistic translation.

Normalized Text:
{text}

Output:"""
