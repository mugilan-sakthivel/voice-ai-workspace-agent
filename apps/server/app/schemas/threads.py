from pydantic import BaseModel


class ThreadCreateRequest(BaseModel):
    user_id: str = "demo-user"
    title: str = "New thread"


class ThreadResponse(BaseModel):
    id: str
    user_id: str
    title: str


class ThreadMessageResponse(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    created_at: str


class ThreadDetailResponse(ThreadResponse):
    messages: list[ThreadMessageResponse]
