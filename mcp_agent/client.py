from mcp_agent.mcp_config import js_mcp_server_params
from typing import AsyncGenerator, List, Optional
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import asyncio
from dotenv import load_dotenv


# Assuming handle_streaming_response is in the same file or correctly imported
# from mcp_agent.stream_handler import handle_streaming_response

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"

async def agent_loop(prompt: str, client: genai.Client, session: ClientSession):
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    # Initialize the connection
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
    
    # --- 2. Initial Request with user prompt and function declarations ---
    # response = await client.aio.models.generate_content(
    #     model=model,  # Or your preferred model supporting function calling
    #     contents=contents,
    #     config=types.GenerateContentConfig(
    #         temperature=0,
    #         tools=[tools],
    #     ),  # Example other config
    # )

    # # --- 3. Append initial response to contents ---
    # # contents.append(response.candidates[0].content)
    # function_calls = response.function_calls
    # print(f"\033[92mfunction_calls:\033[0m {function_calls}")  # Green

    # contents.append(response.candidates[0].content)

    
    stream_response = await client.aio.models._generate_content_stream(
        model=model,  # Or your preferred model supporting function calling
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0,
            tools=[tools],
        ),  # Example other config
    )
    stream_function_calls = None
   
    async for chunk in stream_response:
        # print(chunk.candidates)
        if chunk.candidates[0].content.parts[0].function_call:
             stream_function_calls = [chunk.candidates[0].content.parts[0].function_call]
             print(f"Function call: {stream_function_calls}")
        elif chunk.text:
             print(chunk.text)
             yield {"response": chunk.text}
             contents.append(types.Content(role="user",
                             parts=[types.Part(text=chunk.text)]))
    print(f"\033[94mstream_function_calls:\033[0m {stream_function_calls}")  # Blue

    # --- 4. Tool Calling Loop ---            
    turn_count = 0
    max_tool_turns = 5
    
    if stream_function_calls:
        turn_count += 1
        tool_response_parts: List[types.Part] = []

        # --- 4.1 Process all function calls in order and return in this turn ---
        for fc_part in stream_function_calls:
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
                tool_response = {"error":  f"Tool execution failed: {type(e).__name__}: {e}"}
            
            # Prepare FunctionResponse Part
            tool_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name, response=tool_response
                )
            )

        # --- 4.2 Add the tool response(s) to history ---
        contents.append(types.Content(role="user", parts=tool_response_parts))
        print(f"Added {len(tool_response_parts)} tool response parts to history.")

        # --- 4.3 Make the next call to the model with updated history ---
        print("Making subsequent API call with tool responses...")
        response = await client.aio.models.generate_content_stream(
            model=model,
            contents=contents,  # Send updated history
            config=types.GenerateContentConfig(
                temperature=1.0,
                tools=[tools],
            ),  # Keep sending same config
        )
        async for chunk in response:
            # print(len(chunk.candidates) > 0)
            if chunk.candidates[0].content.parts[0].function_call:
                stream_function_calls = [chunk.candidates[0].content.parts[0].function_call]
                print(f"Function call: {stream_function_calls}")
                yield {"function_call": stream_function_calls}
            elif chunk.text:
                print(chunk.text)
                yield {"response": chunk.text}
                contents.append(types.Content(role="user",
                                parts=[types.Part(text=chunk.text)]))
                
        # contents.append(response.candidates[0].content)

    if turn_count >= max_tool_turns and stream_function_calls:
        print(f"Maximum tool turns ({max_tool_turns}) reached. Exiting loop.")

    print("MCP tool calling loop finished. Returning final response.")
    # --- 5. Return Final Response ---
    return 
        
async def run(prompt):
    async with stdio_client(js_mcp_server_params) as (read, write):
        async with ClientSession(
            read,
            write,
        ) as session:
            # Test prompt
            # prompt = "what is promise"
            print(f"Running agent loop with prompt: {prompt}")
            # Run agent loop
            async for item in agent_loop(prompt, client, session):
                # print(item)
                yield item
           

async def main():
    async for item in run():  # Consume the async generator
        pass 
    # print(res.text)

if __name__ == "__main__":
    asyncio.run(main()) 