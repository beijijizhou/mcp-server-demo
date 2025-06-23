from mcp_agent.client_helper import build_tools, get_stream_repsonse, get_tools_response
from mcp_agent.mcp_config import js_mcp_server_params
from typing import AsyncGenerator, List, Optional
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import asyncio
from dotenv import load_dotenv

from mcp_agent.session_manager import create_session



load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"

conversation_history = []
async def agent_loop(prompt: str, session: ClientSession):
    
    # Initialize the connection
    user_content = types.Content(role="user", parts=[types.Part(text=prompt)])
    conversation_history.append(user_content)

    tools = await build_tools(session)
    response = await get_stream_repsonse(conversation_history, tools)
    stream_function_calls = None
    
    async for chunk in response:
        # print(chunk.candidates)
        if chunk.candidates[0].content.parts[0].function_call:
             stream_function_calls = [chunk.candidates[0].content.parts[0].function_call]
             print(f"function_call: {stream_function_calls}")
             yield {"function_call": stream_function_calls[0].name}

        elif chunk.text:
             print(chunk.text)
             yield {"response": chunk.text}
    conversation_history.append(chunk.candidates[0].content)
    print(conversation_history)
    turn_count = 0
    max_tool_turns = 5
    if not stream_function_calls: return
    if stream_function_calls:
        turn_count += 1
        tool_response_parts = await get_tools_response(stream_function_calls, session)
        yield {"function_call": "finish function call"}
        conversation_history.append(types.Content(role="user", parts=tool_response_parts))
        print(
            f"Added {len(tool_response_parts)} tool response parts to history.")

        # --- 4.3 Make the next call to the model with updated history ---
        print("Making subsequent API call with tool responses...")
        response = await get_stream_repsonse(conversation_history, tools)
        async for chunk in response:
            # print(len(chunk.candidates) > 0)
            if chunk.candidates[0].content.parts[0].function_call:
                stream_function_calls = [
                    chunk.candidates[0].content.parts[0].function_call]
                print(f"Function call: {stream_function_calls}")
                yield {"function_call": stream_function_calls}
            elif chunk.text:
                print(chunk.text)
                # print(chunk.candidates[0].content)
                conversation_history.append(chunk.candidates[0].content)
                yield {"response": chunk.text}
                # contents.append(types.Content(role="user",
                #                 parts=[types.Part(text=chunk.text)]))
        # return

        # contents.append(response.candidates[0].content)
    # print(contents)
    # return 
    if turn_count >= max_tool_turns and stream_function_calls:
        print(f"Maximum tool turns ({max_tool_turns}) reached. Exiting loop.")

    print("MCP tool calling loop finished. Returning final response.")
    # --- 5. Return Final Response ---
    return


async def run(prompt,sessions: Optional[List[ClientSession]] = None) -> AsyncGenerator[dict, None]:
    print("Running agent loop...")
    # print(session)
    async for session in create_session():
        # print(f"Running agent loop with prompt: {prompt}")
        async for item in agent_loop(prompt,  session):
            yield item


