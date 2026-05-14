# agent/workers/cloud.py
import os
from agent.models import ModelManager
from agent.prompts.cloud import CLOUD_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import all_tools

model_manager = ModelManager()

def cloud_node(state):
    model = model_manager.get_model("cloud").bind_tools(all_tools)
    cwd = os.getcwd()
    full_prompt = CLOUD_SYSTEM_PROMPT.format(cwd=cwd)
    messages = [SystemMessage(content=full_prompt)] + state["messages"]
    response = model.invoke(messages)
    response.name = "cloud"
    return {"messages": [response], "current_actor": "cloud"}
