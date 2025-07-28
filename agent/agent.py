import time
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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

def generate_tokens():
    texts = ["pierwszy\n", "drugi\n", "trzeci\n"]
    for t in texts:
        yield t
        time.sleep(1)


async def stream_graph_response(question: str):
    """Async generator for streaming graph response"""
    try:
        result = await graph.ainvoke({"question": question})

        # If a result is iterable, stream it
        if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
            for chunk in result:
                yield str(chunk)
        else:
            # If a result is a single value, yield it as string
            yield str(result)
    except Exception as e:
        yield f"Error: {str(e)}"


@app.post("/invocations")
async def invoke_agent(request: InvocationRequest):
    # return StreamingResponse(generate_tokens())
    try:
        question = request.input.get("question", "")
        if not question:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        return StreamingResponse(
            stream_graph_response(question),
            media_type="text/plain"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")


@app.get("/ping")
async def ping():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
