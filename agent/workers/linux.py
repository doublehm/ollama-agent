import os
from agent.models import ModelManager
from agent.prompts.linux import LINUX_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import all_tools

model_manager = ModelManager()

async def linux_node(state):
    # Get relevant MCP tools from state
    mcp_tools = state.get("mcp_tools", [])
    # For linux, we'll bind all local tools and maybe specific cloud tools if relevant
    
    # Linux specialist uses the 31B model for deep system reasoning
    model = model_manager.get_model("manager").bind_tools(all_tools + mcp_tools)
    
    cwd = os.getcwd()
    full_prompt = LINUX_SYSTEM_PROMPT.format(cwd=cwd)
    
    messages = [SystemMessage(content=full_prompt)] + state["messages"]
    response = await model.ainvoke(messages)
    response.name = "linux"
    return {"messages": [response], "current_actor": "linux"}
