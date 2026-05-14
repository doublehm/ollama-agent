from agent.models import ModelManager
from agent.prompts.manager import MANAGER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import all_tools

model_manager = ModelManager()

# Manager only gets read-only tools for research
READONLY_TOOL_NAMES = {
    "read_file",
    "list_dir",
    "grep",
    "get_processes",
    "web_fetch",
    "web_search",
    "vector_search",
}
readonly_tools = [t for t in all_tools if t.name in READONLY_TOOL_NAMES]

def manager_node(state):
    model = model_manager.get_model("manager")
    model_with_tools = model.bind_tools(readonly_tools)
    messages = [SystemMessage(content=MANAGER_SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(messages)
    response.name = "manager"
    
    # If the manager didn't call a tool, it's likely providing a plan or delegating
    if not response.tool_calls:
        return {"messages": [response], "plan": response.content, "current_actor": "manager"}
    
    return {"messages": [response], "current_actor": "manager"}
