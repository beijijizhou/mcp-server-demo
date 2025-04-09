from mcp_agent.mcp_config import js_mcp_server_params
from typing import AsyncGenerator, List
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import asyncio
from dotenv import load_dotenv

from mcp_agent.stream_handler import handle_streaming_response
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"


async def agent_loop(prompt: str, client: genai.Client, session: ClientSession) -> types.GenerateContentResponse:
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    # Initialize the connection
    try:
        print("Start the session")
        await session.initialize()
    except Exception as e:
        print(f"Error occurred: {e}"),
    print("start the tools")
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
    print("start the prompts")
    function_calls = []
    # --- 2. Initial Request with user prompt and function declarations ---
    async for item in handle_streaming_response(contents, tools, function_calls):
        yield item


    print("Streaming completed successfully")
    return 
    # --- 4. Tool Calling Loop ---
    turn_count = 0
    max_tool_turns = 1
    print(function_calls)
    while function_calls and turn_count < max_tool_turns:
        turn_count += 1
        tool_response_parts: List[types.Part] = []

        # --- 4.1 Process all function calls in order and return in this turn ---
        for fc_part in function_calls:
            tool_name = fc_part.name
            args = fc_part.args or {}  # Ensure args is a dict
            print(
                f"Attempting to call MCP tool: '{tool_name}' with args: {args}")

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

        # --- 4.2 Add the tool response(s) to history ---
        contents.append(types.Content(role="user", parts=tool_response_parts))
        print(
            f"Added {len(tool_response_parts)} tool response parts to history.")

        # --- 4.3 Make the next call to the model with updated history ---
        print("Making subsequent API call with tool responses...")
        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=contents,  # Send updated history
                config=types.GenerateContentConfig(
                    temperature=1.0,
                    tools=[tools],
                ),  # Keep sending same config
            )
            if response.function_calls:
                function_calls = response.function_calls
        except Exception as e:
            print(f"Error generating content: {e}")
            response = None

    if turn_count >= max_tool_turns:
        print(f"Maximum tool turns ({max_tool_turns}) reached. Exiting loop.")

    print("MCP tool calling loop finished. Returning final response.")
    # --- 5. Return Final Response ---


async def run(prompt: str) -> AsyncGenerator[dict, None]:
    try:
        async with stdio_client(js_mcp_server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print(f"Running agent loop with prompt: {prompt}")
                print(f"Client: {client}")
                print(f"Session: {session}")
                print(f"params: {js_mcp_server_params}")
                # Iterate over agent_loop's streamed results
                async for item in agent_loop(prompt, client, session):
                    yield item
    except Exception as e:
        print(f"Error in run: {e}")
        # Return None in case of failure
        yield {"error": f"Run function failed: {str(e)}"}


def main():
    res = asyncio.run(run())


if __name__ == "__main__":
    main()
