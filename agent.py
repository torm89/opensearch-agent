from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from strands import Agent

from discovery_agent.graph import graph

app = FastAPI(title="Strands Agent Server", version="1.0.0")

# Initialize Strands agent
strands_agent = Agent()


class InvocationRequest(BaseModel):
    input: Dict[str, Any]


class InvocationResponse(BaseModel):
    output: Dict[str, Any]


@app.post("/invocations")
async def invoke_agent(request: InvocationRequest):
    try:
        question = request.input.get("question", "")
        if not question:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        stream = graph.ainvoke(question)

        async for event in stream:
            yield event

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")


@app.get("/ping")
async def ping():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
