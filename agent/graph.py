from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.manager import manager_node
from agent.workers.coder import coder_node
from langgraph.prebuilt import ToolNode
from agent.tools import all_tools

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("manager", manager_node)
    builder.add_node("coder", coder_node)
    builder.add_node("tools", ToolNode(all_tools))
    
    # Manager routing: can use read-only tools for research
    def should_continue_manager(state):
        last_msg = state["messages"][-1]
        if last_msg.tool_calls:
            return "tools"
        return "coder"

    builder.add_conditional_edges("manager", should_continue_manager, ["tools", "coder"])
    
    # Coder routing: can use all tools for implementation
    def should_continue_coder(state):
        last_msg = state["messages"][-1]
        if last_msg.tool_calls:
            return "tools"
        return END

    builder.add_conditional_edges("coder", should_continue_coder, ["tools", END])
    
    # Tools routing back to caller based on message name
    def route_after_tools(state):
        # Find the last message that initiated tool calls
        for msg in reversed(state["messages"]):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                if msg.name == "manager":
                    return "manager"
                return "coder"
        return "coder" # Fallback to coder

    builder.add_conditional_edges("tools", route_after_tools, ["manager", "coder"])
    
    # Entry point
    builder.add_edge(START, "manager")
    
    return builder.compile()
