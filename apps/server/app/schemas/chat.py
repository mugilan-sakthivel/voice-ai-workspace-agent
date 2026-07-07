from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    thread_id: str | None = None
    user_id: str = "demo-user"
    message: str
    input_mode: Literal["text", "voice"] = "text"


class ToolProposal(BaseModel):
    id: str = Field(default_factory=lambda: f"tool_{uuid4().hex[:10]}")
    tool_name: str
    summary: str
    requires_approval: bool = False
    arguments: dict = Field(default_factory=dict)


class ApprovalPayload(BaseModel):
    approval_id: str
    action_summary: str
    tool_name: str
    arguments: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    thread_id: str
    message_id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:10]}")
    reply: str
    status: Literal["completed", "approval_required"] = "completed"
    proposed_tools: list[ToolProposal] = Field(default_factory=list)
    approval: ApprovalPayload | None = None

