from pydantic import BaseModel
from typing import Literal

class EmailAnalysis(BaseModel):
    sender: str
    subject: str
    requires_reply: bool
    priority: Literal["low", "medium", "high"]
    suggested_reply: str


class AgentResponse(BaseModel):
    emails: list[EmailAnalysis]
