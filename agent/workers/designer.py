# agent/workers/designer.py
import os
from agent.models import ModelManager
from agent.prompts.designer import DESIGNER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, ToolMessage
from agent.tools import all_tools

model_manager = ModelManager()

async def designer_node(state):
    # Check for images in the message history (most recent tool output ending in .png)
    image_path = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, ToolMessage):
            content = str(msg.content)
            if content.endswith(".png") and os.path.exists(content):
                image_path = content
                break

    cwd = os.getcwd()
    full_prompt = DESIGNER_SYSTEM_PROMPT.format(cwd=cwd)
    messages = [SystemMessage(content=full_prompt)] + state["messages"]

    if image_path:
        # Use the vision model for analysis when an image is present
        # Note: llava usually doesn't support tool calling, so we don't bind tools
        model = model_manager.get_model("vision")
        # Pass the image path to the model via the images parameter
        response = await model.ainvoke(messages, images=[image_path])
    else:
        # Get relevant MCP tools from state
        mcp_tools = state.get("mcp_tools", [])
        relevant_mcp = [t for t in mcp_tools if t.name.startswith("stitch_")]

        # Designer uses the 31B model for general visual/spatial reasoning
        model = model_manager.get_model("designer").bind_tools(all_tools + relevant_mcp)
        response = await model.ainvoke(messages)
    
    response.name = "designer"
    return {"messages": [response], "current_actor": "designer"}
