from typing import AsyncGenerator, List
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"

async def handle_streaming_response(
    contents: List[types.Content],
    tools: types.Tool,
    function_calls: List[types.FunctionCall],
) -> AsyncGenerator[dict, None]:
    """
    Handles streaming responses from generate_content_stream, collecting function calls
    and yielding text responses while updating contents.

    Args:
        client: The Gemini API client.
        model: The model name (e.g., "gemini-2.0-flash").
        contents: List of Content objects to send and update.
        tools: Tool object with function declarations.
        function_calls: List to store detected function calls.

    Yields:
        dict: Streamed response chunks (e.g., {"response": "text"}).
    """

    try:
        response = await client.aio.models.generate_content_stream(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0,
                tools=[tools],
            ),
        )
        async for chunk in response:
            # print(len(chunk.candidates) > 0)
            if chunk.candidates[0].content.parts[0].function_call:
                print(chunk.candidates[0].content.parts[0].function_call)
                function_calls.append(
                    chunk.candidates[0].content.parts[0].function_call)
                # function_calls.append()
            elif chunk.text:
                print(chunk.text)
                yield {"response": chunk.text}
                contents.append(types.Content(role="assistant",
                                parts=[types.Part(text=chunk.text)]))
    except Exception as e:
        print(f"Error during streaming: {e}")
        yield {"error": f"Streaming failed: {str(e)}"}
