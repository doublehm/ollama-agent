# agent/workers/designer.py
import os
from agent.models import ModelManager
from agent.prompts.designer import DESIGNER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import all_tools

model_manager = ModelManager()

def designer_node(state):
    # Designer uses the 70B model for visual/spatial reasoning
    model = model_manager.get_model("designer").bind_tools(all_tools)
    
    cwd = os.getcwd()
    full_prompt = DESIGNER_SYSTEM_PROMPT.format(cwd=cwd)
    
    messages = [SystemMessage(content=full_prompt)] + state["messages"]
    response = model.invoke(messages)
    response.name = "designer"
    return {"messages": [response], "current_actor": "designer"}
