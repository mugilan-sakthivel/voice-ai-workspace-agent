from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.agents.runtime import DemoAgentRuntime
from app.api.dependencies import get_agent_runtime
from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    agent: DemoAgentRuntime = Depends(get_agent_runtime),
) -> ChatResponse:
    thread_id = payload.thread_id or f"thread_{uuid4().hex[:10]}"
    try:
        return await agent.handle_message(
            user_id=payload.user_id,
            thread_id=thread_id,
            message=payload.message,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.websocket("/ws/chat/{thread_id}")
async def chat_ws(
    websocket: WebSocket,
    thread_id: str,
) -> None:
    await websocket.accept()
    try:
        await websocket.send_json(
            {
                "type": "assistant_token",
                "thread_id": thread_id,
                "content": "Streaming is wired. Connect a real frontend to continue this thread.",
            }
        )
        await websocket.send_json({"type": "assistant_final", "thread_id": thread_id})
    except WebSocketDisconnect:
        return
    finally:
        await websocket.close()
