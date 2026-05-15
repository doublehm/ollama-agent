# Universal Expert Assistant: Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal**: Build a functional multi-agent loop where a "Manager" can delegate a coding task to a "Coder" worker, with models being swapped automatically to fit in VRAM.

**Architecture**: A LangGraph-based hierarchical system using a Lead Architect (Llama 70B) for planning and a Developer (Qwen 32B) for execution.

**Tech Stack**: Python 3.12, LangGraph, LangChain, Ollama (Backend), Rich (UI).

---

### Task 1: Project Structure and Dependency Update

**Files**:
- Modify: `pyproject.toml`
- Create: `agent/state.py`

- [ ] **Step 1: Update dependencies**
Add `langchain-mcp-adapters` and ensure `langgraph` versions are current.

```toml
# pyproject.toml changes
dependencies = [
    "langgraph>=1.1",
    "langchain-ollama>=1.1",
    "langchain-core>=1.3",
    "langchain-mcp-adapters>=0.1",
    "ddgs>=8.1",
    "httpx>=0.25",
    "rich>=13.0",
    "prompt_toolkit>=3.0",
    "sentence-transformers>=3.0",
    "faiss-cpu>=1.7",
    "numpy>=1.26",
]
```

- [ ] **Step 2: Define the Expert Agent State**
Create a state schema that supports planning, multiple agents, and context summaries.

```python
# agent/state.py
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
```

- [ ] **Step 3: Commit**
```bash
git add pyproject.toml agent/state.py
git commit -m "chore: setup expert agent state and dependencies"
```

---

### Task 2: Implement the Sequential Model Manager

**Files**:
- Create: `agent/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing test for model swapping**
Verify that we can request a specific model and that it handles the "swapping" concept (simulated via Ollama parameter logic).

```python
# tests/test_models.py
from agent.models import ModelManager

def test_model_resolution():
    manager = ModelManager()
    manager_model = manager.get_model("manager")
    assert manager_model.model == "llama3.3:70b"
    
    coder_model = manager.get_model("coder")
    assert coder_model.model == "qwen2.5-coder:32b"
```

- [ ] **Step 2: Implement the Model Manager**
Implement logic to load models with specific resource constraints for your RTX 4050.

```python
# agent/models.py
from langchain_ollama import ChatOllama

class ModelManager:
    MODELS = {
        "manager": "llama3.3:70b", # IQ-heavy
        "coder": "qwen2.5-coder:32b", # Code-heavy
        "summarizer": "qwen2.5:0.5b" # Background
    }

    def get_model(self, role: str):
        model_name = self.MODELS.get(role, "qwen2.5:latest")
        # Optimization for 6GB VRAM
        # We use num_gpu=0 for the 70B (CPU/RAM) 
        # and partial offload for 32B
        num_gpu = 0 if "70b" in model_name else 30 
        
        return ChatOllama(
            model=model_name,
            temperature=0,
            num_ctx=16384,
            num_gpu=num_gpu,
            keep_alive="5m" # Unload after 5m of inactivity
        )
```

- [ ] **Step 3: Run tests**
`pytest tests/test_models.py`

- [ ] **Step 4: Commit**
```bash
git add agent/models.py tests/test_models.py
git commit -m "feat: implement sequential model manager with VRAM optimizations"
```

---

### Task 3: Build the Lead Architect (Manager) Node

**Files**:
- Create: `agent/manager.py`
- Create: `agent/prompts/manager.py`

- [ ] **Step 1: Define the Architect Prompt**
Ensure the manager focuses on system design and planning rather than execution.

```python
# agent/prompts/manager.py
MANAGER_SYSTEM_PROMPT = """You are the Lead Architect of the Universal Expert Assistant.
Your goal is to take high-level user requests across Linux, DS, Web, and Cloud domains and:
1. Research the current state of the environment.
2. Draft a technical specification and implementation plan.
3. Delegate specific coding or research tasks to specialized workers.

DO NOT write code yourself. Draft the plan first and wait for approval."""
```

- [ ] **Step 2: Implement the Manager Node**
Create a LangGraph node that uses the Architect model to reason and plan.

```python
# agent/manager.py
from agent.models import ModelManager
from agent.prompts.manager import MANAGER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage

model_manager = ModelManager()

def manager_node(state):
    model = model_manager.get_model("manager")
    messages = [SystemMessage(content=MANAGER_SYSTEM_PROMPT)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}
```

- [ ] **Step 3: Commit**
```bash
git add agent/manager.py agent/prompts/manager.py
git commit -m "feat: implement Lead Architect (Manager) node"
```

---

### Task 4: Implement the Developer (Coder) Worker Node

**Files**:
- Create: `agent/workers/coder.py`
- Create: `agent/prompts/coder.py`

- [ ] **Step 1: Define the Coder Prompt**
Focus the Coder on implementing the plan drafted by the Manager.

```python
# agent/prompts/coder.py
CODER_SYSTEM_PROMPT = """You are the Developer Specialist.
Your goal is to implement the technical plan provided by the Lead Architect.
Use the available tools to read, write, and patch files.
Always verify your changes by running tests or lints."""
```

- [ ] **Step 2: Implement the Coder Node**
Use the faster 32B model for this implementation-heavy node.

```python
# agent/workers/coder.py
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
```

- [ ] **Step 3: Commit**
```bash
git add agent/workers/coder.py agent/prompts/coder.py
git commit -m "feat: implement Developer (Coder) worker node"
```

---

### Task 5: Assemble the Multi-Agent Graph

**Files**:
- Modify: `agent/graph.py`

- [ ] **Step 1: Wire the nodes together**
Create the control flow between Manager and Coder.

```python
# agent/graph.py refactor
from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.manager import manager_node
from agent.workers.coder import coder_node
from langgraph.prebuilt import ToolNode
from agent.tools import all_tools

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("manager", manager_node)
    builder.add_node("coder", coder_node)
    builder.add_node("tools", ToolNode(all_tools))
    
    # Simple routing: User -> Manager -> Coder -> Tools -> Coder -> Manager -> User
    builder.add_edge(START, "manager")
    builder.add_edge("manager", "coder")
    
    # Conditional edge for tool use in the Coder
    def should_continue(state):
        last_msg = state["messages"][-1]
        if last_msg.tool_calls:
            return "tools"
        return END

    builder.add_conditional_edges("coder", should_continue, ["tools", END])
    builder.add_edge("tools", "coder")
    
    return builder.compile()
```

- [ ] **Step 2: Verify Graph Compilation**
Run a quick script to ensure the graph compiles without errors.
```python
# check_graph.py
from agent.graph import build_graph
try:
    build_graph()
    print("Graph compiled successfully")
except Exception as e:
    print(f"Graph error: {e}")
```
Run: `python3 check_graph.py`

- [ ] **Step 3: Commit**
```bash
git add agent/graph.py
git commit -m "feat: assemble hierarchical multi-agent graph"
```
