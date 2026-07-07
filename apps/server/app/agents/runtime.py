import re
from datetime import datetime, time, timedelta
from typing import Callable

from app.schemas.chat import ChatResponse, ToolProposal
from app.services.composio import ComposioService
from app.services.store import AppStore


ToolArgsBuilder = Callable[[str], tuple[dict | None, str | None]]


def _contains_keyword(message: str, keyword: str) -> bool:
    return bool(re.search(rf"\b{re.escape(keyword)}\b", message))


def _extract_email_addresses(message: str) -> list[str]:
    return re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", message, flags=re.IGNORECASE)


def _extract_message_payload(message: str) -> str:
    quoted = re.search(r'"([^"]+)"', message)
    if quoted:
        return quoted.group(1).strip()

    for marker in ("saying", "says", "message", "body"):
        match = re.search(rf"\b{marker}\b[:\s]+(.+)$", message, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" .")

    return message.strip()


def _extract_subject(message: str) -> str:
    match = re.search(r"\bsubject\b[:\s]+(.+?)(?:\b(?:body|message|saying)\b[:\s]+|$)", message, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip(" .")

    about_match = re.search(r"\babout\b[:\s]+(.+?)(?:\b(?:to|for|tomorrow|today|at|on)\b|$)", message, flags=re.IGNORECASE)
    if about_match:
        return about_match.group(1).strip(" .")

    return "Message from Voice Agent"


def _build_gmail_send_args(message: str) -> tuple[dict | None, str | None]:
    recipients = _extract_email_addresses(message)
    if not recipients:
        return None, "I can send the email once you give me the recipient email address."

    body = _extract_message_payload(message)
    subject = _extract_subject(message)
    return (
        {
            "recipient_email": recipients[0],
            "extra_recipients": recipients[1:],
            "subject": subject,
            "body": body,
            "user_id": "me",
        },
        None,
    )


def _extract_datetime_from_message(message: str) -> datetime | None:
    now = datetime.now().astimezone()
    iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})[T ](\d{1,2}:\d{2})(?::\d{2})?\b", message)
    if iso_match:
        return datetime.fromisoformat(f"{iso_match.group(1)}T{iso_match.group(2)}").replace(tzinfo=now.tzinfo)

    base_date = None
    lowered = message.lower()
    if "tomorrow" in lowered:
        base_date = (now + timedelta(days=1)).date()
    elif "today" in lowered:
        base_date = now.date()

    time_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", lowered)
    if base_date and time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = time_match.group(3)
        if meridiem == "pm" and hour != 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        return datetime.combine(base_date, time(hour=hour, minute=minute), tzinfo=now.tzinfo)

    return None


def _extract_event_summary(message: str) -> str:
    match = re.search(
        r"\b(?:for|about|called|named)\b[:\s]+(.+?)(?:\b(?:today|tomorrow|on|at|with)\b|$)",
        message,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).strip(" .")
    return "Meeting"


def _build_calendar_create_args(message: str) -> tuple[dict | None, str | None]:
    start_at = _extract_datetime_from_message(message)
    if start_at is None:
        return (
            None,
            "I can schedule that once you give me an exact time, like `tomorrow 3pm` or `2026-04-07 15:00`.",
        )

    return (
        {
            "summary": _extract_event_summary(message),
            "start_datetime": start_at.isoformat(timespec="minutes"),
            "end_datetime": (start_at + timedelta(minutes=30)).isoformat(timespec="minutes"),
            "calendar_id": "primary",
            "attendees": _extract_email_addresses(message),
            "timezone": start_at.tzinfo.tzname(start_at) if start_at.tzinfo else "UTC",
            "create_meeting_room": True,
        },
        None,
    )


def _build_calendar_find_args(message: str) -> tuple[dict | None, str | None]:
    now = datetime.now().astimezone()
    lowered = message.lower()
    day_start = None
    day_end = None

    if "tomorrow" in lowered:
        target_day = (now + timedelta(days=1)).date()
        day_start = datetime.combine(target_day, time.min, tzinfo=now.tzinfo)
        day_end = day_start + timedelta(days=1)
    elif "today" in lowered or "calendar" in lowered:
        target_day = now.date()
        day_start = datetime.combine(target_day, time.min, tzinfo=now.tzinfo)
        day_end = day_start + timedelta(days=1)

    query = re.sub(
        r"\b(show|find|what|is|on|my|calendar|events|event|today|tomorrow|for|please)\b",
        " ",
        lowered,
        flags=re.IGNORECASE,
    )
    query = re.sub(r"\s+", " ", query).strip()

    arguments: dict[str, object] = {
        "calendar_id": "primary",
        "max_results": 10,
        "single_events": True,
        "order_by": "startTime",
    }
    if day_start and day_end:
        arguments["timeMin"] = day_start.isoformat()
        arguments["timeMax"] = day_end.isoformat()
    if query:
        arguments["query"] = query

    return arguments, None


WRITE_HINTS: list[tuple[str, str, str, ToolArgsBuilder]] = [
    ("send", "GMAIL_SEND_EMAIL", "Send an email on the user's behalf", _build_gmail_send_args),
    ("email", "GMAIL_SEND_EMAIL", "Send an email on the user's behalf", _build_gmail_send_args),
    (
        "meeting",
        "GOOGLECALENDAR_CREATE_EVENT",
        "Create a calendar event with attendees",
        _build_calendar_create_args,
    ),
    (
        "schedule",
        "GOOGLECALENDAR_CREATE_EVENT",
        "Create a calendar event with attendees",
        _build_calendar_create_args,
    ),
]

READ_HINTS: list[tuple[str, str, str, ToolArgsBuilder]] = [
    ("calendar", "GOOGLECALENDAR_FIND_EVENT", "Fetch calendar events", _build_calendar_find_args),
]


class DemoAgentRuntime:
    def __init__(self, store: AppStore, composio: ComposioService) -> None:
        self.store = store
        self.composio = composio

    async def handle_message(self, user_id: str, thread_id: str, message: str) -> ChatResponse:
        self.store.ensure_thread(thread_id=thread_id, user_id=user_id)
        self.store.add_message(thread_id=thread_id, role="user", content=message)
        lowered = message.lower()

        for keyword, tool_name, summary, build_args in WRITE_HINTS:
            if _contains_keyword(lowered, keyword):
                arguments, clarification = build_args(message)
                if arguments is None:
                    reply = clarification or "I need a few more details before I can do that."
                    assistant_message = self.store.add_message(
                        thread_id=thread_id,
                        role="assistant",
                        content=reply,
                    )
                    return ChatResponse(
                        thread_id=thread_id,
                        message_id=assistant_message["id"],
                        reply=reply,
                        proposed_tools=[],
                    )

                tool = ToolProposal(
                    tool_name=tool_name,
                    summary=summary,
                    requires_approval=True,
                    arguments=arguments,
                )
                approval = self.store.create_approval(
                    user_id=user_id,
                    thread_id=thread_id,
                    tool_name=tool_name,
                    action_summary=summary,
                    arguments=arguments,
                )
                reply = (
                    "I understood the requested action and paused before executing it. "
                    "Please review the approval card and confirm."
                )
                assistant_message = self.store.add_message(
                    thread_id=thread_id, role="assistant", content=reply
                )
                return ChatResponse(
                    thread_id=thread_id,
                    message_id=assistant_message["id"],
                    reply=reply,
                    status="approval_required",
                    proposed_tools=[tool],
                    approval=approval,
                )

        for keyword, tool_name, summary, build_args in READ_HINTS:
            if _contains_keyword(lowered, keyword):
                arguments, clarification = build_args(message)
                if arguments is None:
                    reply = clarification or "I need a few more details before I can check that."
                    assistant_message = self.store.add_message(
                        thread_id=thread_id,
                        role="assistant",
                        content=reply,
                    )
                    return ChatResponse(
                        thread_id=thread_id,
                        message_id=assistant_message["id"],
                        reply=reply,
                        proposed_tools=[],
                    )

                execution = await self.composio.execute_tool(
                    tool_name,
                    arguments,
                    user_id=user_id,
                )
                reply = (
                    f"I checked the request as a read-only workspace action using `{tool_name}`. "
                    f"{execution['message']}"
                )
                assistant_message = self.store.add_message(
                    thread_id=thread_id, role="assistant", content=reply
                )
                return ChatResponse(
                    thread_id=thread_id,
                    message_id=assistant_message["id"],
                    reply=reply,
                    proposed_tools=[
                        ToolProposal(
                            tool_name=tool_name,
                            summary=summary,
                            requires_approval=False,
                            arguments=arguments,
                        )
                    ],
                )

        reply = (
            "I can help with Gmail and Google Calendar right now. "
            "Try asking me to show your calendar, send an email to an address, or schedule a meeting with a specific time."
        )
        assistant_message = self.store.add_message(
            thread_id=thread_id, role="assistant", content=reply
        )
        return ChatResponse(
            thread_id=thread_id,
            message_id=assistant_message["id"],
            reply=reply,
            proposed_tools=[],
        )
