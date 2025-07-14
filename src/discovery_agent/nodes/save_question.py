from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from discovery_agent.state import HybridState


class Response(BaseModel):
    query: dict = Field(description="The query")


async def save_question(state: HybridState, config: RunnableConfig):

    return {
        "messages": state.messages + [HumanMessage(content=state.question)],
        "action": "Starting",
    }
