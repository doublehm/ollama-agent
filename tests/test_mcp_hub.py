import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from agent.toolkits.mcp_hub import MCPHub

@pytest.mark.asyncio
async def test_mcp_hub_initialization():
    hub = MCPHub("mcp_config.json")
    
    mock_tools = ["tool1", "tool2"]
    mock_client_instance = MagicMock()
    mock_client_instance.get_tools = AsyncMock(return_value=mock_tools)
    
    with patch("agent.toolkits.mcp_hub.MultiServerMCPClient", return_value=mock_client_instance) as mock_client_class:
        tools = await hub.initialize()
        
        assert tools == mock_tools
        assert hub.tools == mock_tools
        mock_client_class.assert_called_once()
        mock_client_instance.get_tools.assert_called_once()

@pytest.mark.asyncio
async def test_mcp_hub_shutdown():
    hub = MCPHub("mcp_config.json")
    mock_client_instance = MagicMock()
    mock_client_instance.close = AsyncMock()
    hub.client = mock_client_instance
    
    await hub.shutdown()
    mock_client_instance.close.assert_called_once()
