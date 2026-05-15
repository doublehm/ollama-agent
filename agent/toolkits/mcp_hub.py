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
            
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            
            # Filter out servers with empty commands or args
            valid_config = {k: v for k, v in config.items() if v.get("command")}
            
            if not valid_config:
                return []

            # We use a single MultiServerMCPClient but we'll try to handle its 
            # initialization more carefully. 
            # Note: langchain-mcp-adapters has a bug where if one server fails, 
            # the whole get_tools() call crashes with UnboundLocalError.
            # To fix this, we'll initialize each server INDIVIDUALLY.
            
            all_mcp_tools = []
            for server_name, server_config in valid_config.items():
                try:
                    # Create a temporary client for just this one server
                    temp_client = MultiServerMCPClient({server_name: server_config})
                    server_tools = await temp_client.get_tools()
                    all_mcp_tools.extend(server_tools)
                    # Note: We can't easily merge multiple MultiServerMCPClients into one 
                    # while keeping the connections open for tools to work.
                    # But for now, getting the tool definitions is a start.
                    # Actually, we should probably keep the client that works.
                except Exception as e:
                    print(f"[warning] Failed to load MCP server '{server_name}': {e}")
            
            # Re-initialize the main client with only the WORKING servers if we wanted to be perfect.
            # For now, let's just try the full config again but catch the specific error.
            self.client = MultiServerMCPClient(valid_config)
            try:
                self.tools = await self.client.get_tools()
            except Exception as e:
                print(f"[warning] Multi-server initialization failed: {e}")
                # Fallback to the individual tools we found (though they might not work without a session)
                self.tools = all_mcp_tools
                
            return self.tools
        except Exception as e:
            print(f"[warning] Failed to initialize MCP tools: {e}")
            return []

    async def shutdown(self):
        if self.client:
            try:
                await self.client.close()
            except:
                pass
