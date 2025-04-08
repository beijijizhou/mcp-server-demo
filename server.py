from mcp_debug import error_display
from vector_db.client import PineconeConnection
error_display()
from mcp.server.fastmcp import FastMCP
import requests
import sys
from typing import Dict, Any

from vector_db.operations import query_vectors
mcp = FastMCP("js_mcp")
print("MCP server is running", file=sys.stderr)
pinecone = PineconeConnection()
print("Vector db is running", file=sys.stderr)

@mcp.resource("vectors://{query_embedding}")
def get_vector_data(query_embedding: str) -> Dict[str, Any]:
    """Retrieve vector database results for a given embedding"""
    print("running vector query")
    return query_vectors(query_embedding)


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
    return 0
@mcp.tool()
def sub(a: int, b: int) -> int:
    """sub two numbers"""
    return a - b - 2