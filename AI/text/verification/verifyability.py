from typing import Dict
from utils.llm import invoke_llm

MODELS = {
    "huggingface": ["deepseek_v3", "llama3_3_70b", "deepseek_r1", "qwen2_5_72b"],
    "claude": ["claude_haiku", "claude_sonnet"]
}

def check_verifyability(text: str) -> Dict:
    prompt = f"""
You classify a statement based ONLY on whether it can be FACT-CHECKED
using independent, external evidence.

You are NOT judging truth or accuracy.
You are NOT assuming access to private records, self-reports, or personal testimony.

A claim must be realistically checkable by an independent verifier
to be considered VERIFYABLE.

====================
DEFINITIONS
====================

A statement is VERIFYABLE if:
- It asserts an objective claim about the real world
AND
- There exists a plausible investigative pathway for an independent party
  to attempt verification using external methods such as public records,
  scientific measurement, historical documentation, journalism,
  or institutional investigation.
- The claim does NOT rely solely on a person's private actions,
  internal records, or self-reporting.
- Claims about public events, known facts, physical properties,
  scientific phenomena, or documented history are VERIFYABLE.
- **Corporate & Event Claims**: Claims about company size, event participants, sales, or public announcements are VERIFYABLE.
- **Facts about Fiction / Pop Culture**: Statements regarding the established canon of books, movies, or games.
- **Broad Statistical/Demographic Claims**: Generalizations that can be measured via polls or studies.
- **Legal & Regulatory Claims**: Statements about rules or laws.
- **Qualitative or Vague Descriptors**: Claims using imprecise descriptors (e.g., "a lot of", "heavy", "many", "often") about real-world measurable events or phenomena are VERIFYABLE. Do not mark them UNVERIFYABLE just because the adjective is subjective.

Examples:
- "Water boils at 100°C at sea level." → VERIFYABLE
- "The Eiffel Tower is in Paris." → VERIFYABLE
- "COVID-19 vaccines were approved in 2020." → VERIFYABLE
- "Most Americans own a smartphone." → VERIFYABLE (Checkable via stats)
- "Murder is illegal in France." → VERIFYABLE (Legal claim)
- "Batman lives in Gotham." → VERIFYABLE (Checkable canon fact)
- "Nepal has a lot of floods due to rain." → VERIFYABLE (Measurable real-world event, despite vague "a lot")

A statement is UNVERIFYABLE if:
- It describes a private personal action, habit, or behavior
  that cannot be independently verified.
- It is a personal feeling, preference, belief, or opinion.
- It refers to internal mental states.
- It lacks sufficient identifiers to locate evidence.
- It is abstract, philosophical, or subjective.
- **Future Predictions & Speculation**: Claims about events that have not yet occurred (since evidence does not exist yet).
- **Moral & Ethical Judgements**: Subjective evaluations of right and wrong.
- **Figures of Speech, Hyperbole & Sarcasm**: Statements not meant to be taken literally.
- **Unfalsifiable Historical Minutiae**: Claims about the distant past involving ordinary people with no possible paper trail.

Examples:
- "I eat bread at night." → UNVERIFYABLE
- "I drank coffee yesterday." → UNVERIFYABLE
- "I like apples." → UNVERIFYABLE
- "He won an award." → UNVERIFYABLE (unclear subject)
- "The stock market will crash in 2030." → UNVERIFYABLE (Future prediction)
- "It is evil to eat meat." → UNVERIFYABLE (Moral judgement)
- "I'm literally dying of laughter right now." → UNVERIFYABLE (Figure of speech)
- "My great-grandfather sneezed on a Tuesday in 1902." → UNVERIFYABLE (Unfalsifiable minutiae)

====================
IMPORTANT RULE
====================

If the statement does not refer to the shared external world
or lacks any identifiable real-world referent,
it MUST be classified as UNVERIFYABLE.

Do NOT classify something as VERIFYABLE merely because it could be
observed in theory or under hypothetical surveillance.

====================
CRITICAL DISTINCTION:

You are classifying the TYPE of claim, not its credibility.

VERIFYABLE means:
The statement refers to the shared external world
(public events, institutions, populations, statistics, physical reality),
such that an independent investigation could in principle be conducted.

VERIFYABLE does NOT require:
- that evidence currently exists
- that numbers are accurate
- that reports are confirmed
- that access is unrestricted

Disputed, exaggerated, propagandistic, or censored claims
can still be VERIFYABLE if they concern public-world facts.

UNVERIFYABLE is reserved ONLY for:
- personal feelings or opinions
- private actions or habits
- internal mental states
- claims lacking any identifiable real-world referent

====================
OUTPUT FORMAT
====================

Output STRICT JSON ONLY:

{{
  "mark": "VERIFYABLE or UNVERIFYABLE",
  "confidence": number between 0 and 100,
  "reason": "very long, detailed explanation"
}}

No extra text.
No markdown.
No commentary.

====================
STATEMENT
====================

{text}
"""
    try:
        data = invoke_llm(MODELS, prompt.strip(), parse_as_json=True)

        mark = data.get("mark", "").upper()
        if mark not in ("VERIFYABLE", "UNVERIFYABLE"):
            mark = "UNVERIFYABLE"

        confidence = max(0, min(int(float(data.get("confidence", 0))), 100))
        reason = data.get("reason", "").strip()

        if len(reason) < 10:
            raise ValueError("Reason too short")

        return {
            "mark": mark,
            "confidence": confidence,
            "reason": reason,
        }

    except Exception as e:
        return {
            "mark": "ERROR",
            "confidence": 0,
            "reason": (
                f"Verifyability check failed due to an internal error ({str(e)}). "
                f"The pipeline will proceed with verification to avoid silently "
                f"dropping a potentially valid claim."
            ),
        }
