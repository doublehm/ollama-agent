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
    model = model_manager.get_model("manager")
    model_with_tools = model.bind_tools(readonly_tools)
    
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
