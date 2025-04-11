from google.genai.types import GenerateContentResponse, Content, Part
from mcp_agent.mcp_config import js_mcp_server_params
from typing import AsyncGenerator, AsyncIterator, List, Optional
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"


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


async def get_repsonse(contents, tools) -> GenerateContentResponse:
    response = await client.aio.models.generate_content(
        model=model,  # Or your preferred model supporting function calling
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0,
            tools=[tools],
        ),
    )
    contents.append(response.candidates[0].content)
    return response


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


async def process_stream_chunk(
    chunk: GenerateContentResponse,
    contents: List[Content]
) -> Optional[dict]:
    """
    Processes a single chunk from the streaming response.

    Args:
        chunk: A GenerateContentResponse object.
        contents: The list of conversation history contents.

    Yields:
        A dictionary containing the text response, if available.
    """
    if chunk.candidates:
        first_candidate = chunk.candidates[0]
        if first_candidate.content and first_candidate.content.parts:
            part = first_candidate.content.parts[0]
            print(part)
            if part.function_call:
                stream_function_calls = [part.function_call]
                print(f"Function call: {stream_function_calls}")
            elif part.text:
                print(part.text)
                contents.append(
                    Content(role="user", parts=[Part(text=part.text)]))
                return {"response": part.text}
    elif hasattr(chunk, 'text') and chunk.text:
        print(chunk.text)
        contents.append(Content(role="user", parts=[Part(text=chunk.text)]))
        return {"response": chunk.text}
    return None


async def handle_streaming_response(
    stream_response: AsyncIterator[GenerateContentResponse],
    contents: List[Content]
) -> AsyncIterator[dict]:
    """
    Asynchronously handles the streaming response from the model.

    Args:
        stream_response: An asynchronous iterator of GenerateContentResponse.
        contents: The list of conversation history contents (will be modified in place).

    Yields:
        Dictionaries containing the text responses from the stream.
    """
    async for chunk in stream_response:
        result = await process_stream_chunk(chunk, contents)
        if result:
            yield result
