import os
from agent.models import ModelManager
from agent.prompts.coder import CODER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import all_tools

model_manager = ModelManager()

async def coder_node(state):
    # Get relevant MCP tools from state
    mcp_tools = state.get("mcp_tools", [])
    relevant_mcp = [t for t in mcp_tools if t.name.startswith("github_")]
    
    # Swap to the Coder model (Qwen 32B)
    model = model_manager.get_model("coder").bind_tools(all_tools + relevant_mcp)
    
    # Enrich prompt with plan and context
    cwd = os.getcwd()
    plan = state.get("plan", "No plan provided yet. Explore the codebase to understand requirements.")
    
    full_prompt = CODER_SYSTEM_PROMPT.format(cwd=cwd, plan=plan)
    
    messages = [SystemMessage(content=full_prompt)] + state["messages"]
    response = await model.ainvoke(messages)
    response.name = "coder"
    return {"messages": [response], "current_actor": "coder"}
