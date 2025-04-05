from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp_config import js_mcp_server_params  # Import params
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


async def run():
    async with stdio_client(js_mcp_server_params) as (read, write):
        async with ClientSession(
            read,
            write,
        ) as session:
            prompt = "promise"
            # Initialize the connection
            await session.initialize()

            # Get tools from MCP session and convert to Gemini Tool objects
            mcp_tools = await session.list_tools()
            tools = types.Tool(function_declarations=[
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
                for tool in mcp_tools.tools
            ])

            # Send request with function declarations
            response = client.models.generate_content(
                model="gemini-2.0-flash",  # Or your preferred model supporting function calling
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    tools=[tools],
                ),  # Example other config
            )
            print(response)
        # Check for a function call
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            print(f"Function to call: {function_call.name}")
            print(f"Arguments: {function_call.args}")
            # In a real app, you would call your function here:
            result = await session.call_tool(
                name=function_call.name,  # Tool name as string
                arguments=function_call.args  # Arguments dictionary
            )            # sent new request with function call
        else:
            print("No function call found in the response.")
            print(response.text)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
