
from typing import AsyncGenerator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_agent.mcp_config import js_mcp_server_params
global_session: ClientSession | None = None


        
async def create_session() -> AsyncGenerator[ClientSession, None]:
    """
    Creates a ClientSession within the context of a stdio client.
    """
    async with stdio_client(js_mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            yield session