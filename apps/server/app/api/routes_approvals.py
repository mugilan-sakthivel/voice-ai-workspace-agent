from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_composio_service, get_store


router = APIRouter(tags=["approvals"])


class ApprovalResolutionRequest(BaseModel):
    user_id: str = "demo-user"


class ApprovalResolutionResponse(BaseModel):
    approval_id: str
    status: str
    message: str


@router.post("/approvals/{approval_id}/confirm", response_model=ApprovalResolutionResponse)
async def confirm_approval(
    approval_id: str,
    payload: ApprovalResolutionRequest,
) -> ApprovalResolutionResponse:
    store = get_store()
    composio = get_composio_service()
    context = store.get_approval_context(approval_id)
    approval = store.get_approval(approval_id)
    if approval is None or context is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    if context["user_id"] != payload.user_id:
        raise HTTPException(status_code=403, detail="Approval does not belong to this user")
    if context.get("status") != "pending":
        raise HTTPException(status_code=409, detail="Approval has already been resolved")
    result = await composio.execute_tool(approval.tool_name, approval.arguments, user_id=context["user_id"])
    if not result.get("success", False):
        store.add_message(
            thread_id=context["thread_id"],
            role="assistant",
            content="Approval was granted, but the workspace action failed to execute.",
        )
        raise HTTPException(status_code=502, detail=result.get("message", "Workspace action failed"))
    store.resolve_approval(approval_id, "approved")
    confirmation_text = (
        "Approval confirmed. The requested workspace action was simulated in dry-run mode."
        if result.get("dry_run")
        else "Approval confirmed. The requested workspace action was triggered."
    )
    store.add_message(
        thread_id=context["thread_id"],
        role="assistant",
        content=confirmation_text,
    )
    return ApprovalResolutionResponse(
        approval_id=approval.approval_id,
        status="approved",
        message=confirmation_text,
    )


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalResolutionResponse)
async def reject_approval(
    approval_id: str,
    payload: ApprovalResolutionRequest,
) -> ApprovalResolutionResponse:
    store = get_store()
    context = store.get_approval_context(approval_id)
    approval = store.get_approval(approval_id)
    if approval is None or context is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    if context["user_id"] != payload.user_id:
        raise HTTPException(status_code=403, detail="Approval does not belong to this user")
    if context.get("status") != "pending":
        raise HTTPException(status_code=409, detail="Approval has already been resolved")
    store.resolve_approval(approval_id, "rejected")
    store.add_message(
        thread_id=context["thread_id"],
        role="assistant",
        content="Approval rejected. No write action was performed.",
    )
    return ApprovalResolutionResponse(
        approval_id=approval.approval_id,
        status="rejected",
        message="Approval rejected. No write action was performed.",
    )
