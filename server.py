from mcp.server.fastmcp import FastMCP
import sys
import os

# Print Python version
print(f"Python Version: {sys.version}",file=sys.stderr)

# Print Virtual Environment (if any)
venv = os.environ.get("VIRTUAL_ENV")
if venv:
    print(f"Virtual Environment: {venv}",file=sys.stderr)
else:
    print("No Virtual Environment Active", file=sys.stderr)
import requests
from typing import Dict, Any
mcp = FastMCP("Demo2")


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
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
@mcp.tool()
def sub(a: int, b: int) -> int:
    """sub two numbers"""
    return a - b