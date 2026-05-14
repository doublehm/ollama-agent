from agent.models import ModelManager
from agent.prompts.manager import MANAGER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage

model_manager = ModelManager()

def manager_node(state):
    model = model_manager.get_model("manager")
    messages = [SystemMessage(content=MANAGER_SYSTEM_PROMPT)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}
