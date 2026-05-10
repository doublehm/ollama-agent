import os

from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from agent.prompts import build_system_prompt
from agent.tools import all_tools


def build_graph(model_name: str = "gemma4:latest", cwd: str | None = None):
    if cwd is None:
        cwd = os.getcwd()
    model = ChatOllama(model=model_name, temperature=0)
    system_prompt = SystemMessage(content=build_system_prompt(cwd=cwd))
    return create_react_agent(model, tools=all_tools, prompt=system_prompt)
