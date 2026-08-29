import logging
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END

from summary.summarizer import summarize
from verification.factcheck import fact_check
from verification.verifyability import check_verifyability
from verification.decompose import decompose_claims
from websearch.web_verify import web_verify

logger = logging.getLogger(__name__)


TEST_STOP_AFTER = None

class GraphState(TypedDict):
    statement: str
    summary: str
    claims: list[str]
    result: Optional[dict[str, Any]]

def summarize_node(state: GraphState):
    logger.info("Executing summarize_node")
    summary = summarize(state["statement"])
    return {"summary": summary}

def verifyability_node(state: GraphState):
    logger.info("Executing verifyability_node")
    res = check_verifyability(state["summary"])
    return {"result": res}

def decompose_node(state: GraphState):
    logger.info("Executing decompose_node")
    claims = decompose_claims(state["summary"])
    return {"claims": claims}

def verify_claims_node(state: GraphState):
    logger.info("Executing verify_claims_node")
    claims = state.get("claims")
    if not claims:
        claims = [state["summary"]]
    
    results = []
    for claim in claims:
        res = fact_check(claim)
        if res.get("mark") == "Insufficient":
            res = web_verify(claim)
        results.append((claim, res))
        
    final_mark = "Correct"
    overall_confidence = 0
    reasons = []
    urls = []
    
    has_incorrect = False
    has_insufficient = False
    
    for claim, res in results:
        mark = res.get("mark")
        conf = res.get("confidence", 0)
        
        if len(claims) > 1:
            reasons.append(f"Claim: '{claim}'\nVerdict: {mark} ({conf}% confidence)\nReason: {res.get('reason', '')}")
        else:
            reasons.append(res.get('reason', ''))
            
        overall_confidence += conf
        if res.get("urls"):
            urls.extend(res.get("urls"))
            
        if mark == "Incorrect":
            has_incorrect = True
        elif mark == "Insufficient":
            has_insufficient = True
            
    if has_incorrect:
        final_mark = "Incorrect"
    elif has_insufficient:
        final_mark = "Insufficient"
        
    avg_conf = overall_confidence // len(results) if results else 0
    urls = list(set(urls))
    
    return {"result": {
        "mark": final_mark,
        "confidence": avg_conf,
        "reason": "\n\n---\n\n".join(reasons) if len(claims) > 1 else reasons[0],
        "urls": urls
    }}

def should_continue_verifyability(state: GraphState):
    res = state.get("result")
    if res and res.get("mark") == "ERROR":
        logger.info("Verifyability check encountered an error. Falling through to decompose.")
        return "decompose"
    if res and res.get("mark") == "UNVERIFYABLE":
        logger.info("Claim is UNVERIFYABLE. Ending pipeline.")
        return END
    logger.info("Claim is VERIFYABLE. Proceeding to decompose.")
    return "decompose"


builder = StateGraph(GraphState)
builder.add_node("summarize", summarize_node)
builder.add_node("verifyability", verifyability_node)
builder.add_node("decompose", decompose_node)
builder.add_node("verify_claims", verify_claims_node)

builder.add_edge(START, "summarize")

if TEST_STOP_AFTER == "summarize":
    builder.add_edge("summarize", END)
else:
    builder.add_edge("summarize", "verifyability")
    
    if TEST_STOP_AFTER == "verifyability":
        builder.add_edge("verifyability", END)
    else:
        builder.add_conditional_edges("verifyability", should_continue_verifyability)
        builder.add_edge("decompose", "verify_claims")
        builder.add_edge("verify_claims", END)

workflow = builder.compile()

def verify_text(statement: str):
    if not statement:
        return {
            "summary": "",
            "result": {
                "mark": "ERROR",
                "confidence": 0,
                "reason": "Input text is missing or empty."
            }
        }
        
    logger.info(f"Starting text verification for statement: {statement[:50]}...")
    initial_state = {"statement": statement, "summary": "", "claims": [], "result": None}
    
    try:
        final_state = workflow.invoke(initial_state)
        return {
            "summary": final_state.get("summary"),
            "result": final_state.get("result")
        }
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return {
            "summary": statement,
            "result": {
                "mark": "ERROR",
                "confidence": 0,
                "reason": f"Pipeline execution failed: {e}"
            }
        }
