from fastapi import APIRouter, HTTPException

from app.api.dependencies import get_store
from app.schemas.threads import (
    ThreadCreateRequest,
    ThreadDetailResponse,
    ThreadMessageResponse,
    ThreadResponse,
)


router = APIRouter(tags=["threads"])


@router.get("/threads", response_model=list[ThreadResponse])
async def list_threads(user_id: str = "demo-user") -> list[ThreadResponse]:
    store = get_store()
    return [ThreadResponse(**thread) for thread in store.list_threads(user_id)]


@router.post("/threads", response_model=ThreadResponse)
async def create_thread(payload: ThreadCreateRequest) -> ThreadResponse:
    store = get_store()
    return ThreadResponse(**store.create_thread(payload.user_id, payload.title))


@router.get("/threads/{thread_id}", response_model=ThreadDetailResponse)
async def get_thread(thread_id: str, user_id: str = "demo-user") -> ThreadDetailResponse:
    store = get_store()
    thread = store.find_thread(thread_id, user_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = [ThreadMessageResponse(**message) for message in store.list_messages(thread_id)]
    return ThreadDetailResponse(**thread, messages=messages)
