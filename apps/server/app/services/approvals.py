from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4


ApprovalStatus = Literal["pending", "approved", "rejected"]


@dataclass
class ApprovalRecord:
    id: str
    user_id: str
    thread_id: str
    tool_name: str
    action_summary: str
    arguments: dict = field(default_factory=dict)
    status: ApprovalStatus = "pending"


class ApprovalStore:
    def __init__(self) -> None:
        self._approvals: dict[str, ApprovalRecord] = {}

    def create(
        self, user_id: str, thread_id: str, tool_name: str, action_summary: str, arguments: dict
    ) -> ApprovalRecord:
        record = ApprovalRecord(
            id=f"apr_{uuid4().hex[:10]}",
            user_id=user_id,
            thread_id=thread_id,
            tool_name=tool_name,
            action_summary=action_summary,
            arguments=arguments,
        )
        self._approvals[record.id] = record
        return record

    def get(self, approval_id: str) -> ApprovalRecord | None:
        return self._approvals.get(approval_id)

    def resolve(self, approval_id: str, status: ApprovalStatus) -> ApprovalRecord | None:
        record = self._approvals.get(approval_id)
        if record is None:
            return None
        record.status = status
        return record

