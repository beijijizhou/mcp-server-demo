from mcp import ClientSession, StdioServerParameters
import os
env = os.getenv("ENV", "local")  # Default to "local" if ENV is not set
command = "uv" if env == "local" else "python"
print(command, env)
js_mcp_server_params = StdioServerParameters(
    command="python",  # Executable
    args=[
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "server.py"
    ],  # Optional command line arguments
    env={
        "PINECONE_API_KEY": "pcsk_R5zga_U4X3anECzPmCdT9enskjoGJE7FKUG6qte9LM9PtNWbYXM9Vc6BCFUVYYxxqrjJC",
        "PINECONE_ENV": "us-east-1-aws",
        "PINECONE_INDEX_NAME": "testing"
    },  # Optional environment variables
)
