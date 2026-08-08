import logging
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END

from summary.summarizer import summarize
from verification.factcheck import fact_check
from verification.verifyability import check_verifyability
from websearch.web_verify import web_verify

logger = logging.getLogger(__name__)


TEST_STOP_AFTER = None

class GraphState(TypedDict):
    statement: str
    summary: str
    result: Optional[dict[str, Any]]

def summarize_node(state: GraphState):
    logger.info("Executing summarize_node")
    summary = summarize(state["statement"])
    return {"summary": summary}

def verifyability_node(state: GraphState):
    logger.info("Executing verifyability_node")
    res = check_verifyability(state["summary"])
    return {"result": res}

def fact_check_node(state: GraphState):
    logger.info("Executing fact_check_node")
    res = fact_check(state["summary"])
    return {"result": res}

def web_verify_node(state: GraphState):
    logger.info("Executing web_verify_node")
    res = web_verify(state["summary"])
    return {"result": res}

def should_continue_verifyability(state: GraphState):
    res = state.get("result")
    if res and res.get("mark") == "UNVERIFYABLE":
        logger.info("Claim is UNVERIFYABLE. Ending pipeline.")
        return END
    logger.info("Claim is VERIFYABLE. Proceeding to fact_check.")
    return "fact_check"

def should_continue_fact_check(state: GraphState):
    res = state.get("result")
    if res and res.get("mark") == "Insufficient":
        logger.info("Fact check Insufficient. Proceeding to web_verify.")
        return "web_verify"
    logger.info("Fact check sufficient. Ending pipeline.")
    return END


builder = StateGraph(GraphState)
builder.add_node("summarize", summarize_node)
builder.add_node("verifyability", verifyability_node)
builder.add_node("fact_check", fact_check_node)
builder.add_node("web_verify", web_verify_node)

builder.add_edge(START, "summarize")

if TEST_STOP_AFTER == "summarize":
    builder.add_edge("summarize", END)
else:
    builder.add_edge("summarize", "verifyability")
    
    if TEST_STOP_AFTER == "verifyability":
        builder.add_edge("verifyability", END)
    else:
        builder.add_conditional_edges("verifyability", should_continue_verifyability)
        
        if TEST_STOP_AFTER == "fact_check":
            builder.add_edge("fact_check", END)
        else:
            builder.add_conditional_edges("fact_check", should_continue_fact_check)
            builder.add_edge("web_verify", END)

workflow = builder.compile()

def verify_text(statement: str):
    logger.info(f"Starting text verification for statement: {statement[:50]}...")
    initial_state = {"statement": statement, "summary": "", "result": None}
    
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
