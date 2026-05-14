import json
import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPHub:
    def __init__(self, config_path="mcp_config.json"):
        self.config_path = config_path
        self.client = None
        self.tools = []

    async def initialize(self):
        if not os.path.exists(self.config_path):
            return []
            
        with open(self.config_path) as f:
            config = json.load(f)
        
        # MultiServerMCPClient takes a dict of server configs
        self.client = MultiServerMCPClient(config)
        self.tools = await self.client.get_tools()
        return self.tools

    async def shutdown(self):
        if self.client:
            await self.client.close()
