from typing import Annotated, TypedDict, List, Any
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Standard message history
    messages: Annotated[list[AnyMessage], add_messages]
    # The validated implementation plan from the Manager
    plan: str
    # Results from sub-agents
    worker_outputs: List[str]
    # Current active domain (e.g., 'linux', 'web', 'ds')
    active_domain: str
    # The original goal from the user
    root_goal: str
    # The current active node/actor in the graph
    current_actor: str
