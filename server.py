from mcp.server.fastmcp import FastMCP
import requests
import sys
from typing import Dict, Any
mcp = FastMCP("js_mcp")
print("MCP server is running", file=sys.stderr)

@mcp.resource("vectors://{query_embedding}")
def get_vector_data(query_embedding: str) -> Dict[str, Any]:
    """Retrieve vector database results for a given embedding"""
    rag_api_url = "http://localhost:5000/embed"

    try:
        response = requests.post(rag_api_url, json={"texts": [query_embedding]})
        response.raise_for_status()  # Raise an error for HTTP errors (4xx, 5xx)
        return response.json()  # Directly return the parsed JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@mcp.tool()
def query_vector_database(user_prompt: str) -> Dict[str, Any]:
    """Fetch vector data based on user input when it is JavaScript related"""
    embedding_response = get_vector_data(user_prompt)
    print(embedding_response, file= sys.stderr)
    if "error" in embedding_response:
        return {"error": f"Failed to fetch embedding: {embedding_response['error']}"}

    return embedding_response
    

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
@mcp.tool()
def sub(a: int, b: int) -> int:
    """sub two numbers"""
    return a - b