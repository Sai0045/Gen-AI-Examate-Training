from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from app.agent_loop import select_tool, execute_tool


class AgentState(TypedDict):
    question: str
    decision: Optional[dict]
    result: Optional[dict]
    approved: bool


def select_node(state: AgentState):
    decision = select_tool(state["question"])

    return {"decision": decision}


def approval_node(state: AgentState):
    approved = interrupt({
        "message": "Approve execution of the selected tool?",
        "tool": state["decision"]["tool"]
    })

    return {"approved": bool(approved)}


def execute_node(state: AgentState):
    result = execute_tool(
        state["decision"],
        state["question"]
    )

    return {"result": result}


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("select_tool", select_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("execute_tool", execute_node)

    workflow.add_edge(START, "select_tool")
    workflow.add_edge("select_tool", "approval")
    workflow.add_conditional_edges(
        "approval",
        lambda state: "execute" if state["approved"] else "stop",
        {
            "execute": "execute_tool",
            "stop": END
        }
    )
    workflow.add_edge("execute_tool", END)

    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)


agent_graph = build_graph()
