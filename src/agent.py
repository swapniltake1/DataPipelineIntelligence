"""Diagnosis workflow with optional LangGraph orchestration."""
from typing import TypedDict
from .diagnosis import diagnose

class DiagnosisState(TypedDict, total=False):
    error_text: str
    status: str
    diagnosis: object

def _diagnose_node(state: DiagnosisState) -> DiagnosisState:
    return {"diagnosis": diagnose(state.get("error_text", ""), state.get("status", "Failed"))}

def build_diagnosis_graph():
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return None
    graph = StateGraph(DiagnosisState)
    graph.add_node("diagnose", _diagnose_node)
    graph.add_edge(START, "diagnose")
    graph.add_edge("diagnose", END)
    return graph.compile()

_GRAPH = build_diagnosis_graph()

def run_diagnosis(error_text: str, status: str = "Failed"):
    if _GRAPH is None:
        return diagnose(error_text, status)
    return _GRAPH.invoke({"error_text": error_text or "", "status": status})["diagnosis"]
