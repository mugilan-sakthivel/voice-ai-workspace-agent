from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select

from app.db import (
    ApprovalRecordDB,
    ConnectedAccountRecord,
    Database,
    MessageRecord,
    ThreadRecord,
    get_messages_for_thread,
    get_thread_by_id,
    touch_thread,
)
from app.schemas.chat import ApprovalPayload
from app.schemas.integrations import ConnectedAccount


class AppStore:
    def __init__(self, database: Database) -> None:
        self.database = database
        self._threads: dict[str, dict] = {}
        self._messages: dict[str, list[dict]] = {}
        self._approvals: dict[str, ApprovalPayload] = {}
        self._approval_contexts: dict[str, dict] = {}
        self._accounts: dict[str, list[ConnectedAccount]] = {}

    def create_thread(self, user_id: str, title: str = "New thread") -> dict:
        thread_id = f"thread_{uuid4().hex[:10]}"
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    record = ThreadRecord(id=thread_id, user_id=user_id, title=title)
                    session.add(record)
                    return {"id": record.id, "user_id": record.user_id, "title": record.title}

        thread = {"id": thread_id, "user_id": user_id, "title": title}
        self._threads[thread_id] = thread
        self._messages.setdefault(thread_id, [])
        return thread

    def ensure_thread(self, thread_id: str, user_id: str, title: str = "New thread") -> dict:
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    existing = get_thread_by_id(session, thread_id)
                    if existing is None:
                        existing = ThreadRecord(id=thread_id, user_id=user_id, title=title)
                        session.add(existing)
                    elif existing.user_id != user_id:
                        raise PermissionError("Thread does not belong to this user")
                    return {"id": existing.id, "user_id": existing.user_id, "title": existing.title}

        thread = self._threads.get(thread_id)
        if thread is None:
            thread = {"id": thread_id, "user_id": user_id, "title": title}
            self._threads[thread_id] = thread
            self._messages.setdefault(thread_id, [])
        elif thread["user_id"] != user_id:
            raise PermissionError("Thread does not belong to this user")
        return thread

    def find_thread(self, thread_id: str, user_id: str) -> dict | None:
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    existing = get_thread_by_id(session, thread_id)
                    if existing is None or existing.user_id != user_id:
                        return None
                    return {"id": existing.id, "user_id": existing.user_id, "title": existing.title}

        thread = self._threads.get(thread_id)
        if thread is None or thread["user_id"] != user_id:
            return None
        return thread

    def list_threads(self, user_id: str) -> list[dict]:
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    stmt = select(ThreadRecord).where(ThreadRecord.user_id == user_id).order_by(ThreadRecord.updated_at.desc())
                    return [
                        {"id": record.id, "user_id": record.user_id, "title": record.title}
                        for record in session.scalars(stmt).all()
                    ]
        return [thread for thread in self._threads.values() if thread["user_id"] == user_id]

    def add_message(self, thread_id: str, role: str, content: str) -> dict:
        message = {
            "id": f"msg_{uuid4().hex[:10]}",
            "thread_id": thread_id,
            "role": role,
            "content": content,
            "created_at": datetime.now(UTC).isoformat(),
        }
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    thread = get_thread_by_id(session, thread_id)
                    if thread is not None:
                        touch_thread(thread)
                    session.add(
                        MessageRecord(
                            id=message["id"],
                            thread_id=thread_id,
                            role=role,
                            content=content,
                        )
                    )
                    return message

        self._messages.setdefault(thread_id, []).append(message)
        return message

    def list_messages(self, thread_id: str) -> list[dict]:
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    return [
                        {
                            "id": item.id,
                            "thread_id": item.thread_id,
                            "role": item.role,
                            "content": item.content,
                            "created_at": item.created_at.isoformat(),
                        }
                        for item in get_messages_for_thread(session, thread_id)
                    ]
        return self._messages.get(thread_id, [])

    def create_approval(
        self, user_id: str, thread_id: str, tool_name: str, action_summary: str, arguments: dict
    ) -> ApprovalPayload:
        approval = ApprovalPayload(
            approval_id=f"apr_{uuid4().hex[:10]}",
            action_summary=action_summary,
            tool_name=tool_name,
            arguments=arguments,
        )
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    session.add(
                        ApprovalRecordDB(
                            id=approval.approval_id,
                            user_id=user_id,
                            thread_id=thread_id,
                            tool_name=tool_name,
                            action_summary=action_summary,
                            arguments=arguments,
                        )
                    )
                    return approval
        self._approvals[approval.approval_id] = approval
        self._approval_contexts[approval.approval_id] = {
            "user_id": user_id,
            "thread_id": thread_id,
            "tool_name": tool_name,
            "action_summary": action_summary,
            "arguments": arguments,
            "status": "pending",
        }
        return approval

    def get_approval(self, approval_id: str) -> ApprovalPayload | None:
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    record = session.get(ApprovalRecordDB, approval_id)
                    if record is None:
                        return None
                    return ApprovalPayload(
                        approval_id=record.id,
                        action_summary=record.action_summary,
                        tool_name=record.tool_name,
                        arguments=record.arguments or {},
                    )
        return self._approvals.get(approval_id)

    def resolve_approval(self, approval_id: str, status: str) -> ApprovalPayload | None:
        approval = self.get_approval(approval_id)
        if approval is None:
            return None
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    record = session.get(ApprovalRecordDB, approval_id)
                    if record is not None:
                        record.status = status
                        record.resolved_at = datetime.now(UTC)
                        return approval
        if approval_id in self._approval_contexts:
            self._approval_contexts[approval_id]["status"] = status
        return approval

    def get_approval_context(self, approval_id: str) -> dict | None:
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    record = session.get(ApprovalRecordDB, approval_id)
                    if record is None:
                        return None
                    return {
                        "approval_id": record.id,
                        "user_id": record.user_id,
                        "thread_id": record.thread_id,
                        "tool_name": record.tool_name,
                        "action_summary": record.action_summary,
                        "arguments": record.arguments or {},
                        "status": record.status,
                    }
        return self._approval_contexts.get(approval_id)

    def upsert_connected_account(
        self,
        user_id: str,
        suite: str,
        app: str,
        status: str,
        connected_account_id: str | None = None,
        auth_config_id: str | None = None,
    ) -> ConnectedAccount:
        account = ConnectedAccount(
            suite=suite,
            app=app,
            status=status,
            connected_account_id=connected_account_id or f"{app}::{user_id}",
        )
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    account_id = f"acct_{suite}_{app}_{user_id}".replace("-", "_")
                    record = session.get(ConnectedAccountRecord, account_id)
                    if record is None:
                        record = ConnectedAccountRecord(
                            id=account_id,
                            user_id=user_id,
                            suite=suite,
                            app=app,
                        )
                        session.add(record)
                    record.status = status
                    record.connected_account_id = connected_account_id
                    record.auth_config_id = auth_config_id
                    record.updated_at = datetime.now(UTC)
                    return account

        existing = self._accounts.setdefault(user_id, [])
        replacement = [item for item in existing if not (item.suite == suite and item.app == app)]
        replacement.append(account)
        self._accounts[user_id] = replacement
        return account

    def list_connected_accounts(self, user_id: str) -> list[ConnectedAccount]:
        if self.database.available:
            with self.database.session() as session:
                if session is not None:
                    stmt = select(ConnectedAccountRecord).where(ConnectedAccountRecord.user_id == user_id)
                    return [
                        ConnectedAccount(
                            suite=record.suite,
                            app=record.app,
                            status=record.status,
                            connected_account_id=record.connected_account_id or f"{record.app}::{user_id}",
                        )
                        for record in session.scalars(stmt).all()
                    ]
        return self._accounts.get(user_id, [])
