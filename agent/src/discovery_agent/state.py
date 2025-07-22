from __future__ import annotations

from typing import Optional, Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel


class InputState(BaseModel):
    question: str


class HybridState(InputState):
    messages: Annotated[list, add_messages]
    action: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
