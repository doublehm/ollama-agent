from agent.models import ModelManager
from agent.prompts.coder import CODER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import all_tools

model_manager = ModelManager()

def coder_node(state):
    # Swap to the Coder model (Qwen 32B)
    model = model_manager.get_model("coder").bind_tools(all_tools)
    messages = [SystemMessage(content=CODER_SYSTEM_PROMPT)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}
