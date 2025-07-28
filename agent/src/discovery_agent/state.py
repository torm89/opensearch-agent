from __future__ import annotations

from typing import Optional, Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel


class InputState(BaseModel):
    question: str

    opensearch_host: str
    opensearch_region: str
    opensearch_service: str = "es"



class HybridState(InputState):
    messages: Annotated[list, add_messages]
    action: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
