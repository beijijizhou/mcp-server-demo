
from typing import AsyncGenerator
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


global_session: ClientSession | None = None

async def initialize_session(js_mcp_server_params: dict) -> ClientSession:
    """
    Creates and initializes a ClientSession.
    """
    async with stdio_client(js_mcp_server_params) as (read, write):
        session = ClientSession(read, write)
        # await session.initialize()
        # return session

async def get_global_session() -> ClientSession:
    """
    Returns the globally initialized session. Initializes it if it doesn't exist.
    """
    global global_session
    if global_session is None:
        # Replace with your actual js_mcp_server_params
        global_session = await initialize_session({})
    return global_session

async def close_global_session():
    """
    Closes the global session if it exists and has a close method.
    """
    global global_session
    if global_session and hasattr(global_session, 'close') and callable(getattr(global_session, 'close')):
        await global_session.close()
        global_session = None
        print("Global session closed.")
    elif global_session:
        global_session = None
        print("Global session reset (no close method).")
        
async def create_session(js_mcp_server_params: dict) -> AsyncGenerator[ClientSession, None]:
    """
    Creates a ClientSession within the context of a stdio client.
    """
    async with stdio_client(js_mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            yield session