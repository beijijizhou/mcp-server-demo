from google.genai.types import GenerateContentResponse, Content, Part
from mcp_agent.mcp_config import js_mcp_server_params
from typing import AsyncGenerator, AsyncIterator, List, Optional
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import asyncio
import functools
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"
import time
from typing import Callable, Any, Coroutine
def measure_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@measure_time
async def build_tools(session: ClientSession):
    await session.initialize()
    # --- 1. Get Tools from Session and convert to Gemini Tool objects ---
    mcp_tools = await session.list_tools()
    tools = types.Tool(function_declarations=[
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema,
        }
        for tool in mcp_tools.tools
    ])
    return tools

@measure_time
async def get_stream_repsonse(contents, tools):
    stream_response = await client.aio.models.generate_content_stream(
        model=model,  # Or your preferred model supporting function calling
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0,
            tools=[tools],
        ),
    )

    return stream_response


@measure_time
async def get_tools_response(function_calls, session):
    tool_response_parts: List[types.Part] = []
    # --- 4.1 Process all function calls in order and return in this turn ---
    for fc_part in function_calls:
        tool_name = fc_part.name
        args = fc_part.args or {}  # Ensure args is a dict
        print(f"Attempting to call MCP tool: '{tool_name}' with args: {args}")
        tool_response: dict
        try:
            # Call the session's tool executor
            tool_result = await session.call_tool(tool_name, args)
            print(f"MCP tool '{tool_name}' executed successfully.")
            if tool_result.isError:
                tool_response = {"error": tool_result.content[0].text}
            else:
                tool_response = {"result": tool_result.content[0].text}
        except Exception as e:
            tool_response = {
                "error":  f"Tool execution failed: {type(e).__name__}: {e}"}

        # Prepare FunctionResponse Part
        tool_response_parts.append(
            types.Part.from_function_response(
                name=tool_name, response=tool_response
            )
        )
        return tool_response_parts


