from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from mcp_agent.client import run

app = FastAPI()

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

@app.post("/query")
async def query_endpoint(query: QueryRequest):
    if not query.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    print(query)
    try:
        result = await run(query.prompt)
        # Verify result has expected attribute
        if not hasattr(result, 'text'):
            raise ValueError("Invalid response format from run function")
        return {
            "response": result.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
@app.get("/")
async def root():
    return {"message": "Welcome to the API", "status": "ok"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000)