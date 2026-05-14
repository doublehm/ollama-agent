from agent.models import ModelManager
from agent.prompts.manager import MANAGER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from agent.tools import readonly_tools

model_manager = ModelManager()

DOMAIN_KEYWORDS = {
    "ds": ["data", "model", "train", "pandas", "pytorch", "plot", "visualization"],
    "design": ["ui", "ux", "css", "tailwind", "compose", "layout", "styling", "component"],
    "cloud": ["terraform", "kubectl", "kubernetes", "cloud", "aws", "gcp", "devops"],
    "linux": ["systemd", "journalctl", "service", "hardware", "cpu", "gpu", "kernel", "linux"],
}

def classify_domain(text: str) -> str:
    text = text.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return domain
    return "general"

def manager_node(state):
    # Get relevant MCP tools from state (readonly ones for manager)
    mcp_tools = state.get("mcp_tools", [])
    # Heuristic: tools that don't sound like "create", "delete", "write", "update"
    # For now, we'll just bind them all but the prompt tells it to research.
    # Official readonly heuristic usually involves checking tool schema for side-effects,
    # but we'll stick to local tools + all mcp tools for research.
    
    model = model_manager.get_model("manager")
    model_with_tools = model.bind_tools(readonly_tools + mcp_tools)
    
    # Add domain instruction
    prompt_with_instructions = MANAGER_SYSTEM_PROMPT + "\n\nCRITICAL: Identify the domain in your response (ds, design, cloud, linux, or general)."
    
    messages = [SystemMessage(content=prompt_with_instructions)] + state["messages"]
    response = model_with_tools.invoke(messages)
    response.name = "manager"
    
    # Detect domain from response content
    content = response.content.lower()
    detected_domain = classify_domain(content)
    # If explicitly stated in response, override
    for d in DOMAIN_KEYWORDS.keys():
        if f"domain: {d}" in content:
            detected_domain = d
            
    active_domain = state.get("active_domain", "general")
    if detected_domain != "general":
        active_domain = detected_domain

    result = {
        "messages": [response], 
        "current_actor": "manager",
        "active_domain": active_domain
    }
    
    if not response.tool_calls:
        result["plan"] = response.content
        
    return result
