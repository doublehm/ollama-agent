# agent/workers/cloud.py
import os
from agent.models import ModelManager
from agent.prompts.cloud import CLOUD_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import all_tools

model_manager = ModelManager()

async def cloud_node(state):
    # Get relevant MCP tools from state
    mcp_tools = state.get("mcp_tools", [])
    relevant_mcp = [t for t in mcp_tools if t.name.startswith("gcp_")]

    model = model_manager.get_model("cloud").bind_tools(all_tools + relevant_mcp)
    cwd = os.getcwd()
    full_prompt = CLOUD_SYSTEM_PROMPT.format(cwd=cwd)
    messages = [SystemMessage(content=full_prompt)] + state["messages"]
    response = await model.ainvoke(messages)
    response.name = "cloud"
    return {"messages": [response], "current_actor": "cloud"}
