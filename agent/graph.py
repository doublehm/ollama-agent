from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.manager import manager_node
from agent.workers.coder import coder_node
from agent.workers.scientist import scientist_node
from agent.workers.designer import designer_node
from agent.workers.cloud import cloud_node
from agent.workers.linux import linux_node
from langgraph.prebuilt import ToolNode
from agent.tools import all_tools

def build_graph(mcp_tools=None):
    builder = StateGraph(AgentState)
    mcp_tools = mcp_tools or []
    
    # Add nodes
    builder.add_node("manager", manager_node)
    builder.add_node("coder", coder_node)
    builder.add_node("scientist", scientist_node)
    builder.add_node("designer", designer_node)
    builder.add_node("cloud", cloud_node)
    builder.add_node("linux", linux_node)
    builder.add_node("tools", ToolNode(all_tools + mcp_tools))
    
    # Manager routing: can use read-only tools for research, then route to specialist
    def route_from_manager(state):
        last_msg = state["messages"][-1]
        if last_msg.tool_calls:
            return "tools"
        
        domain = state.get("active_domain", "general")
        if domain == "ds":
            return "scientist"
        if domain == "design":
            return "designer"
        if domain == "cloud":
            return "cloud"
        if domain == "linux":
            return "linux"
        return "coder" # default to general developer

    builder.add_conditional_edges("manager", route_from_manager, ["tools", "scientist", "designer", "cloud", "linux", "coder"])
    
    # Specialized Worker routing (all use same logic: tools or END)
    def should_continue_worker(state):
        last_msg = state["messages"][-1]
        if last_msg.tool_calls:
            return "tools"
        return END

    for node in ["coder", "scientist", "designer", "cloud", "linux"]:
        builder.add_conditional_edges(node, should_continue_worker, ["tools", END])
    
    # Tools routing back to caller based on state['current_actor']
    def route_after_tools(state):
        return state.get("current_actor", "coder")

    builder.add_conditional_edges("tools", route_after_tools, ["manager", "coder", "scientist", "designer", "cloud", "linux"])
    
    # Entry point
    builder.add_edge(START, "manager")
    
    return builder.compile()
