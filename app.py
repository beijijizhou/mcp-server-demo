from contextlib import asynccontextmanager
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from mcp_agent.client import run
@asynccontextmanager
async def lifespan(app: FastAPI):
    global global_session
    # Startup: Initialize the session
    # Replace with your actual js_mcp_server_params
    # global_session = await initialize_session({})
    print("ClientSession initialized on startup (using lifespan).")
    yield
    # Shutdown: Clean up resources if needed
    if global_session:
        # Example of potential cleanup (if your ClientSession has a close method)
        # await global_session.close()
        print("ClientSession shutdown (if applicable).")
        global_session = None

app = FastAPI(lifespan=lifespan)


# More specific CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://js-interview-green.vercel.app"],
    allow_credentials=True,  # Allows cookies/auth headers
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


class QueryRequest(BaseModel):
    prompt: str

async def stream_response(prompt: str):
    async for item in run(prompt):
        yield json.dumps(item) + "\n"

@app.post("/query")
async def query_endpoint(query: QueryRequest):
    if not query.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    print(query)
    return StreamingResponse(stream_response(query.prompt), media_type="text/event-stream")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
@app.get("/")
async def root():
    return {"message": "Welcome to the API", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000)