# Voice AI Workspace Agent - Final Architecture (v2)

## Document Info
- **Version:** 2.0
- **Date:** 2024-01-15
- **Status:** Architecture Finalized

---

## 1. Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Voice Input | **Push-to-talk** (v1) | iOS background audio is unreliable; simpler, better UX |
| STT Provider | **Groq Whisper** | 216x real-time speed, $0.04/hour, best latency |
| TTS Provider | **Gemini 2.5 Flash TTS** | 30 voices, natural speech, good quality |
| AI Framework | **DeepAgents** (built on LangGraph) | Planning, memory, subagents, tool calling |
| Workspace | **Google first** | Then add Microsoft 365 |
| Platform | **Mobile only** (iOS + Android) | React Native + Expo |
| UI Framework | **assistant-ui** | Claude-like interface, LangGraph runtime built-in |
| Multi-user CLI | **Token injection per request** | Isolated subprocess with user's token |

---

## 2. Final System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              VOICE AI WORKSPACE AGENT                                │
│                                  SYSTEM ARCHITECTURE                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           MOBILE APP (React Native + Expo)                          │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                          assistant-ui (LangGraph Runtime)                    │   │
│  │                                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Thread     │  │  Composer    │  │   Message    │  │  Tool Call   │    │   │
│  │  │   View       │  │  Bar         │  │   Bubble     │  │  Display     │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  │                                                                              │   │
│  │  Built-in: Streaming | Thread Management | Checkpointing | Tool UI          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                           │                                         │
│  ┌──────────────────────┐                 │                                         │
│  │  Push-to-Talk Voice  │                 │                                         │
│  │  ┌────────────────┐  │                 │                                         │
│  │  │ 🎤 Hold to     │  │  Records audio  │                                         │
│  │  │    Speak       │  │  ─────────────> │                                         │
│  │  └────────────────┘  │                 │                                         │
│  │  expo-av recording   │                 │                                         │
│  └──────────────────────┘                 │                                         │
│                                           │                                         │
│  ┌──────────────────────┐                 │                                         │
│  │  Audio Playback      │                 │                                         │
│  │  (TTS Response)      │ <───────────────┘                                         │
│  │  expo-av player      │                                                           │
│  └──────────────────────┘                                                           │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  State Management (Zustand)                                                   │  │
│  │  - Auth tokens (secure store)  - Settings  - Conversation state              │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTPS / WebSocket
                                          │ JWT in Authorization header
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI + LangGraph)                          │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                              API GATEWAY                                      │  │
│  │                                                                               │  │
│  │  REST Endpoints:                        WebSocket:                            │  │
│  │  ├── POST /api/v1/voice/stt            ├── /ws/chat/{thread_id}              │  │
│  │  │    └─> Groq Whisper                 │    └─> LangGraph streaming          │  │
│  │  ├── POST /api/v1/voice/tts            │                                      │  │
│  │  │    └─> Gemini TTS                   │                                      │  │
│  │  ├── POST /api/v1/auth/google          │                                      │  │
│  │  ├── GET  /api/v1/threads              │                                      │  │
│  │  └── GET  /api/v1/threads/{id}         │                                      │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                          │                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                         VOICE PROCESSING LAYER                                │  │
│  │                                                                               │  │
│  │  ┌─────────────────────────────┐    ┌─────────────────────────────┐          │  │
│  │  │      GROQ WHISPER STT       │    │      GEMINI TTS             │          │  │
│  │  │                             │    │                             │          │  │
│  │  │  Model: whisper-large-v3-   │    │  Model: gemini-2.5-flash-   │          │  │
│  │  │         turbo               │    │         preview-tts         │          │  │
│  │  │  Speed: 216x real-time      │    │  Voices: 30 options         │          │  │
│  │  │  Cost: $0.04/hour           │    │  Default: "Kore"            │          │  │
│  │  │  Latency: ~100ms            │    │  Languages: 77              │          │  │
│  │  └─────────────────────────────┘    └─────────────────────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                          │                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                            LANGGRAPH AGENT                                    │  │
│  │                                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                         AGENT GRAPH                                      │ │  │
│  │  │                                                                          │ │  │
│  │  │   ┌─────────┐      ┌─────────────┐      ┌─────────────┐                 │ │  │
│  │  │   │  START  │─────>│   Agent     │─────>│   Tools     │                 │ │  │
│  │  │   └─────────┘      │  (Gemini)   │      │  Execution  │                 │ │  │
│  │  │                    │             │<─────│             │                 │ │  │
│  │  │                    │  - Parse    │      │  - Drive    │                 │ │  │
│  │  │                    │  - Decide   │      │  - Gmail    │                 │ │  │
│  │  │                    │  - Respond  │      │  - Calendar │                 │ │  │
│  │  │                    └─────────────┘      │  - Sheets   │                 │ │  │
│  │  │                          │              │  - Docs     │                 │ │  │
│  │  │                          ▼              └─────────────┘                 │ │  │
│  │  │                    ┌─────────┐                                          │ │  │
│  │  │                    │   END   │                                          │ │  │
│  │  │                    └─────────┘                                          │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                               │  │
│  │  LLM: Gemini 2.0 Flash (gemini-2.0-flash)                                    │  │
│  │  Checkpointer: PostgresSaver (conversation persistence)                       │  │
│  │  Streaming: Yes (messages + updates)                                          │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                          │                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                      CLI EXECUTION ENGINE (Multi-User)                        │  │
│  │                                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    REQUEST ISOLATION MODEL                               │ │  │
│  │  │                                                                          │ │  │
│  │  │   User A Request ──┐                                                     │ │  │
│  │  │                    │     ┌─────────────────────────────────┐             │ │  │
│  │  │                    ├────>│  Subprocess Pool                │             │ │  │
│  │  │                    │     │                                 │             │ │  │
│  │  │   User B Request ──┤     │  ┌───────────────────────────┐ │             │ │  │
│  │  │                    │     │  │ Worker 1                  │ │             │ │  │
│  │  │                    │     │  │ ENV: GOOGLE_..._TOKEN=A   │ │             │ │  │
│  │  │   User C Request ──┘     │  │ gws calendar +agenda      │ │             │ │  │
│  │  │                          │  └───────────────────────────┘ │             │ │  │
│  │  │                          │                                 │             │ │  │
│  │  │                          │  ┌───────────────────────────┐ │             │ │  │
│  │  │                          │  │ Worker 2                  │ │             │ │  │
│  │  │                          │  │ ENV: GOOGLE_..._TOKEN=B   │ │             │ │  │
│  │  │                          │  │ gws gmail +send ...       │ │             │ │  │
│  │  │                          │  └───────────────────────────┘ │             │ │  │
│  │  │                          │                                 │             │ │  │
│  │  │                          │  ┌───────────────────────────┐ │             │ │  │
│  │  │                          │  │ Worker N                  │ │             │ │  │
│  │  │                          │  │ ENV: GOOGLE_..._TOKEN=C   │ │             │ │  │
│  │  │                          │  │ gws drive files list      │ │             │ │  │
│  │  │                          │  └───────────────────────────┘ │             │ │  │
│  │  │                          └─────────────────────────────────┘             │ │  │
│  │  │                                                                          │ │  │
│  │  │   Key: Each subprocess gets user's token via ENV var                     │ │  │
│  │  │   Isolation: Token never shared between users                            │ │  │
│  │  │   Concurrency: asyncio.create_subprocess_exec() - non-blocking           │ │  │
│  │  │   Cleanup: Subprocess terminates after command, token cleared            │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                               │  │
│  │  Google Workspace CLI (gws): Installed globally in Docker container          │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                          OAUTH & TOKEN MANAGEMENT                             │  │
│  │                                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                      TOKEN LIFECYCLE                                     │ │  │
│  │  │                                                                          │ │  │
│  │  │   1. User connects Google ──> OAuth code                                 │ │  │
│  │  │   2. Backend exchanges ──> access_token + refresh_token                  │ │  │
│  │  │   3. Encrypt with Fernet ──> Store in PostgreSQL                         │ │  │
│  │  │   4. On each request:                                                    │ │  │
│  │  │      - Check token expiry (with 5min buffer)                             │ │  │
│  │  │      - If expired: refresh token automatically                           │ │  │
│  │  │      - Decrypt token                                                     │ │  │
│  │  │      - Inject into subprocess ENV                                        │ │  │
│  │  │      - Execute CLI command                                               │ │  │
│  │  │      - Token cleared when subprocess exits                               │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA LAYER                                         │
│                                                                                     │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────────────┐  │
│  │     PostgreSQL        │  │        Redis          │  │   Google Workspace     │  │
│  │                       │  │                       │  │   APIs                 │  │
│  │  - users              │  │  - session cache      │  │                        │  │
│  │  - oauth_credentials  │  │  - rate limiting      │  │  - Gmail API           │  │
│  │  - threads            │  │  - token cache        │  │  - Calendar API        │  │
│  │  - checkpoints        │  │    (short-lived)      │  │  - Drive API           │  │
│  │    (LangGraph)        │  │                       │  │  - Sheets API          │  │
│  └───────────────────────┘  └───────────────────────┘  │  - Docs API            │  │
│                                                         └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Multi-User CLI Execution (Detailed)

This is the **critical architecture decision** for handling concurrent users.

### 3.1 The Challenge

When 100 users are using the app simultaneously:
- Each user has their own Google OAuth token
- CLI commands must use the correct user's token
- Tokens must never leak between users
- Must handle concurrent requests efficiently

### 3.2 The Solution: Process Isolation with Token Injection

```python
# services/cli_executor.py

import asyncio
import os
from typing import Optional
import json

class CLIExecutor:
    """
    Executes CLI commands in isolated subprocesses with user-specific tokens.

    Key principles:
    1. Each command runs in its own subprocess
    2. Token is passed via environment variable (never stored in process memory long-term)
    3. Subprocess terminates immediately after command completes
    4. Async execution allows concurrent commands from different users
    """

    def __init__(self, oauth_service: OAuthService):
        self.oauth_service = oauth_service
        self.semaphore = asyncio.Semaphore(50)  # Max 50 concurrent CLI executions

    async def execute_google_command(
        self,
        user_id: str,
        command: str,
        timeout: int = 30
    ) -> CLIResult:
        """
        Execute a Google Workspace CLI command for a specific user.

        Args:
            user_id: The user's ID (to fetch their token)
            command: The gws command (e.g., "drive files list --params '{...}'")
            timeout: Command timeout in seconds

        Returns:
            CLIResult with stdout, stderr, and success status
        """

        async with self.semaphore:  # Limit concurrent executions
            try:
                # 1. Get user's valid access token (auto-refreshes if needed)
                access_token = await self.oauth_service.get_google_access_token(user_id)

                # 2. Create isolated environment with user's token
                env = {
                    **os.environ,
                    "GOOGLE_WORKSPACE_CLI_TOKEN": access_token,
                    # Prevent any credential file usage
                    "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE": "",
                }

                # 3. Execute command in subprocess
                process = await asyncio.create_subprocess_exec(
                    "gws",
                    *command.split(),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                )

                # 4. Wait for completion with timeout
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    return CLIResult(
                        success=False,
                        error="Command timed out",
                        stdout="",
                        stderr=""
                    )

                # 5. Parse result
                if process.returncode == 0:
                    try:
                        output = json.loads(stdout.decode())
                    except json.JSONDecodeError:
                        output = stdout.decode()

                    return CLIResult(
                        success=True,
                        output=output,
                        stdout=stdout.decode(),
                        stderr=stderr.decode()
                    )
                else:
                    return CLIResult(
                        success=False,
                        error=stderr.decode() or "Command failed",
                        stdout=stdout.decode(),
                        stderr=stderr.decode()
                    )

            except OAuthError as e:
                return CLIResult(
                    success=False,
                    error=f"Authentication error: {str(e)}",
                    stdout="",
                    stderr=""
                )
            except Exception as e:
                return CLIResult(
                    success=False,
                    error=f"Execution error: {str(e)}",
                    stdout="",
                    stderr=""
                )


@dataclass
class CLIResult:
    success: bool
    output: Optional[dict] = None
    error: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
```

### 3.3 Why This Architecture?

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Subprocess per request** | ✅ Perfect isolation, ✅ Token never persists, ✅ Simple | ⚠️ Process overhead | **CHOSEN** |
| Container per user | ✅ Strong isolation | ❌ Very expensive, ❌ Slow startup | Too heavy |
| Shared process, token switching | ✅ Fast | ❌ Race conditions, ❌ Token leakage risk | Risky |
| gws as library (not CLI) | ✅ No subprocess overhead | ❌ gws is CLI only | Not possible |

### 3.4 Concurrency Model

```
Incoming requests:
  User A ─┐
  User B ─┼──> Async Queue ──> Semaphore (max 50) ──> Subprocess Pool
  User C ─┤                                               │
  User D ─┘                                               ▼
                                                    ┌─────────────┐
                                                    │ Worker 1    │
                                                    │ User A token│
                                                    │ gws ...     │
                                                    └─────────────┘
                                                    ┌─────────────┐
                                                    │ Worker 2    │
                                                    │ User B token│
                                                    │ gws ...     │
                                                    └─────────────┘
                                                          ...
```

---

## 4. assistant-ui ↔ FastAPI Integration

### 4.1 Connection Architecture

assistant-ui has a **LangGraph runtime** that connects to LangGraph-compatible backends. We'll use this pattern:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND-BACKEND CONNECTION                           │
└─────────────────────────────────────────────────────────────────────────┘

Mobile App (assistant-ui)                    FastAPI Backend
┌─────────────────────────┐                 ┌─────────────────────────────┐
│                         │                 │                             │
│  useLangGraphRuntime({  │                 │  @app.websocket("/ws/chat") │
│    stream: async (msg)  │ ═══════════════>│  async def chat_ws(...):    │
│      => sendMessage()   │   WebSocket     │    # LangGraph streaming    │
│    create: async ()     │   + JWT Auth    │                             │
│      => createThread()  │                 │  @app.post("/api/threads")  │
│  })                     │ ───────────────>│  async def create_thread(): │
│                         │   REST + JWT    │    # Create LangGraph thread│
└─────────────────────────┘                 └─────────────────────────────┘
```

### 4.2 Mobile App Runtime Setup

```typescript
// hooks/useChatRuntime.ts

import { useLangGraphRuntime } from '@assistant-ui/react';
import { useAuthStore } from '../store/authStore';

// API Client with auth
const createApiClient = () => {
  const token = useAuthStore.getState().sessionToken;

  return {
    async createThread(): Promise<{ thread_id: string }> {
      const response = await fetch(`${API_URL}/api/v1/threads`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      return response.json();
    },

    async *streamChat(
      threadId: string,
      messages: Message[],
      command?: LangGraphCommand
    ): AsyncGenerator<StreamEvent> {
      // WebSocket connection with auth
      const ws = new WebSocket(
        `${WS_URL}/ws/chat/${threadId}?token=${token}`
      );

      // Send message
      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: 'chat',
          messages,
          command,
        }));
      };

      // Yield streaming events
      const eventQueue: StreamEvent[] = [];
      let resolve: (() => void) | null = null;

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        eventQueue.push(data);
        if (resolve) {
          resolve();
          resolve = null;
        }
      };

      ws.onerror = (error) => {
        eventQueue.push({ type: 'error', error });
      };

      ws.onclose = () => {
        eventQueue.push({ type: 'end' });
      };

      // Async generator pattern
      while (true) {
        if (eventQueue.length === 0) {
          await new Promise<void>((r) => { resolve = r; });
        }

        const event = eventQueue.shift()!;
        if (event.type === 'end') break;
        if (event.type === 'error') throw event.error;

        yield event;
      }
    },
  };
};

// Runtime hook for assistant-ui
export const useChatRuntime = () => {
  const api = createApiClient();

  return useLangGraphRuntime({
    // Create new conversation thread
    create: async () => {
      const { thread_id } = await api.createThread();
      return { externalId: thread_id };
    },

    // Stream chat messages
    stream: async function* (messages, { initialize, command }) {
      const { externalId } = await initialize();

      for await (const event of api.streamChat(externalId, messages, command)) {
        yield event;
      }
    },
  });
};
```

### 4.3 FastAPI WebSocket Handler

```python
# api/websocket.py

from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
import json

@app.websocket("/ws/chat/{thread_id}")
async def websocket_chat(
    websocket: WebSocket,
    thread_id: str,
    token: str = Query(...),  # JWT token in query param
    db: Session = Depends(get_db),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    WebSocket endpoint for streaming chat with LangGraph agent.

    Protocol:
    1. Client connects with JWT token
    2. Client sends: {"type": "chat", "messages": [...]}
    3. Server streams: {"type": "message_chunk", "content": "..."}
    4. Server streams: {"type": "tool_call", "tool": "...", "status": "..."}
    5. Server sends: {"type": "end"}
    """

    # Verify JWT token
    try:
        user = verify_jwt_token(token)
    except InvalidTokenError:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    # Initialize LangGraph agent with user's tools
    agent = await create_agent_for_user(user.id, oauth_service)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            if data.get("type") == "chat":
                messages = data.get("messages", [])

                # Stream agent response
                async for event in agent.astream(
                    {"messages": messages},
                    config={"configurable": {"thread_id": thread_id}},
                    stream_mode=["messages", "updates"]
                ):
                    # Handle different event types
                    if "messages" in event:
                        for msg in event["messages"]:
                            await websocket.send_json({
                                "type": "message_chunk",
                                "content": msg.content,
                                "role": msg.type,
                            })

                    if "updates" in event:
                        for node, update in event["updates"].items():
                            if "tool_calls" in update:
                                for tool_call in update["tool_calls"]:
                                    await websocket.send_json({
                                        "type": "tool_call",
                                        "tool": tool_call["name"],
                                        "args": tool_call["args"],
                                        "status": "executing",
                                    })

                            if "tool_results" in update:
                                for result in update["tool_results"]:
                                    await websocket.send_json({
                                        "type": "tool_result",
                                        "tool": result["name"],
                                        "result": result["output"],
                                        "success": result.get("success", True),
                                    })

                # Signal end of response
                await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
```

---

## 5. DeepAgents Implementation

### 5.0 What is DeepAgents?

**DeepAgents** is LangChain's agent harness built on top of LangGraph. It provides:

| Feature | Description |
|---------|-------------|
| **Planning** | Built-in `write_todos` tool for task decomposition |
| **Context Management** | Virtual filesystem tools (ls, read_file, write_file, edit_file) |
| **Subagents** | Spawn specialized agents for isolated subtasks |
| **Persistent Memory** | Cross-conversation storage via LangGraph Memory Store |
| **Pluggable Backends** | Swappable implementations (in-memory, local, sandboxed) |

### Why DeepAgents for Voice Agent?

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      DEEPAGENTS vs BASIC LANGGRAPH AGENT                             │
└─────────────────────────────────────────────────────────────────────────────────────┘

BASIC LANGGRAPH AGENT:
┌─────────┐     ┌─────────────┐     ┌─────────┐
│  User   │────>│   Agent     │────>│  Tool   │
│  Input  │     │  (1 step)   │     │  Call   │
└─────────┘     └─────────────┘     └─────────┘

DEEPAGENTS:
┌─────────┐     ┌─────────────────────────────────────────────────────┐
│  User   │────>│                   DEEP AGENT                        │
│  Input  │     │                                                     │
└─────────┘     │  ┌───────────┐   ┌────────────────────────────────┐│
                │  │  PLANNER  │──>│ TODO LIST                       ││
                │  │           │   │ 1. Check calendar for conflicts ││
                │  │ Breaks    │   │ 2. Find John's email            ││
                │  │ task into │   │ 3. Create meeting event         ││
                │  │ steps     │   │ 4. Send confirmation            ││
                │  └───────────┘   └────────────────────────────────┘│
                │        │                                            │
                │        ▼                                            │
                │  ┌───────────┐   ┌───────────┐   ┌───────────┐     │
                │  │ Execute   │──>│ Execute   │──>│ Execute   │     │
                │  │ Step 1    │   │ Step 2    │   │ Step 3... │     │
                │  └───────────┘   └───────────┘   └───────────┘     │
                │        │                                            │
                │        ▼                                            │
                │  ┌───────────────────────────────────────────────┐ │
                │  │  MEMORY STORE (Persistent across sessions)    │ │
                │  │  - User preferences                           │ │
                │  │  - Previous interactions                      │ │
                │  │  - Context from past conversations            │ │
                │  └───────────────────────────────────────────────┘ │
                └─────────────────────────────────────────────────────┘
```

**Benefits for Voice Agent:**

1. **Complex Tasks**: "Schedule a meeting with John, check my calendar first, and send him an email" → DeepAgent breaks this into steps
2. **Memory**: Remembers user preferences ("I prefer morning meetings")
3. **Plan Adaptation**: If step fails, can re-plan automatically
4. **Concise Responses**: Knows full plan, can summarize effectively for voice

### 5.1 DeepAgent Implementation

```python
# agent/deep_agent.py

from deepagents import create_deep_agent
from deepagents.tools import write_todos
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

def create_voice_agent(
    user_id: str,
    oauth_service: OAuthService,
    db_connection_string: str
):
    """
    Create a DeepAgent for voice-activated workspace management.

    DeepAgents provides:
    - Built-in planning (write_todos)
    - Persistent memory across sessions
    - Subagent spawning for complex tasks
    """

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
    )

    # Create workspace tools with user's credentials
    cli_executor = CLIExecutor(oauth_service)
    workspace_tools = [
        # Calendar tools
        create_get_agenda_tool(user_id, cli_executor),
        create_create_event_tool(user_id, cli_executor),
        create_list_events_tool(user_id, cli_executor),

        # Gmail tools
        create_list_emails_tool(user_id, cli_executor),
        create_send_email_tool(user_id, cli_executor),
        create_search_emails_tool(user_id, cli_executor),

        # Drive tools
        create_list_files_tool(user_id, cli_executor),
        create_search_files_tool(user_id, cli_executor),
        create_share_file_tool(user_id, cli_executor),

        # Sheets tools
        create_read_sheet_tool(user_id, cli_executor),
        create_append_sheet_tool(user_id, cli_executor),

        # Docs tools
        create_read_doc_tool(user_id, cli_executor),
        create_create_doc_tool(user_id, cli_executor),
    ]

    # System prompt optimized for voice interaction
    system_prompt = """You are a voice-activated AI assistant that manages Google Workspace.

## Your Capabilities
- **Calendar**: View agenda, create/update/delete events, check availability
- **Gmail**: Read, send, search, and organize emails
- **Drive**: List, search, share, and organize files
- **Sheets**: Read data, append rows, update cells
- **Docs**: Read and create documents

## Voice Interaction Guidelines
1. **Be Concise**: Your responses will be spoken aloud. Keep them brief and clear.
2. **Confirm Actions**: Always confirm before sending emails or deleting anything.
3. **Summarize Results**: Don't read entire emails/documents. Summarize key points.
4. **Handle Failures Gracefully**: If something fails, explain briefly and suggest alternatives.

## Planning Complex Tasks
For multi-step requests like "Schedule a meeting with John and send him the agenda":
1. Use the planning capability to break into steps
2. Execute each step
3. Provide a single, concise summary at the end

## Memory
You have persistent memory. Remember:
- User's preferences (meeting times, email signatures, etc.)
- Frequently contacted people
- Common file locations

Current date: {date}
User's timezone: {timezone}
User ID: {user_id}"""

    # Create the DeepAgent
    agent = create_deep_agent(
        model=llm,
        tools=workspace_tools,
        system_prompt=system_prompt.format(
            date="{date}",
            timezone="{timezone}",
            user_id=user_id
        ),
        # Enable planning for complex tasks
        enable_planning=True,
        # Checkpointer for conversation persistence
        checkpointer=PostgresSaver.from_conn_string(db_connection_string),
        # Memory store for long-term memory
        store=PostgresStore.from_conn_string(db_connection_string),
    )

    return agent


# ============================================
# USING THE AGENT
# ============================================

async def handle_user_message(
    user_id: str,
    thread_id: str,
    message: str,
    oauth_service: OAuthService,
    db_connection_string: str
):
    """Handle a user message with the DeepAgent."""

    # Create agent for this user
    agent = create_voice_agent(user_id, oauth_service, db_connection_string)

    # Configuration with thread ID for conversation continuity
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id,
        }
    }

    # Stream the response
    async for event in agent.astream(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
        stream_mode=["messages", "updates", "custom"]
    ):
        yield event


# ============================================
# EXAMPLE: COMPLEX TASK WITH PLANNING
# ============================================

"""
User: "Schedule a team meeting for tomorrow, check everyone's availability,
       and send them the meeting link with the agenda"

DeepAgent Planning:
┌─────────────────────────────────────────────────────────┐
│ TODO LIST (auto-generated by DeepAgent)                 │
├─────────────────────────────────────────────────────────┤
│ 1. ☐ Get list of team members from recent emails       │
│ 2. ☐ Check calendar availability for tomorrow          │
│ 3. ☐ Find common free time slot                        │
│ 4. ☐ Create calendar event with all attendees          │
│ 5. ☐ Get the meeting link from created event           │
│ 6. ☐ Compose email with agenda and meeting link        │
│ 7. ☐ Send email to all team members                    │
│ 8. ☐ Summarize what was done                           │
└─────────────────────────────────────────────────────────┘

Execution:
Step 1: gws gmail users messages list --params '{"q": "to:team"}'
Step 2: gws calendar freebusy query ...
Step 3: [Internal reasoning]
Step 4: gws +insert --summary "Team Meeting" --attendees "..."
Step 5: [Extract from step 4 result]
Step 6: [Compose message]
Step 7: gws +send --to "..." --subject "Team Meeting Tomorrow" --body "..."
Step 8: [Generate voice-friendly summary]

Final Response (spoken):
"Done! I've scheduled a team meeting for tomorrow at 2 PM.
 I sent the meeting link and agenda to Sarah, Mike, and Alex."
"""
```

### 5.2 DeepAgent with Memory

```python
# agent/memory.py

from langgraph.store.postgres import PostgresStore

class VoiceAgentMemory:
    """
    Persistent memory for the voice agent.

    Stores:
    - User preferences
    - Frequently contacted people
    - Common queries
    - Learned patterns
    """

    def __init__(self, store: PostgresStore, user_id: str):
        self.store = store
        self.user_id = user_id
        self.namespace = ("voice_agent", user_id)

    async def save_preference(self, key: str, value: any):
        """Save a user preference."""
        await self.store.put(
            self.namespace,
            f"preference:{key}",
            {"value": value}
        )

    async def get_preference(self, key: str, default=None):
        """Get a user preference."""
        item = await self.store.get(self.namespace, f"preference:{key}")
        return item.value["value"] if item else default

    async def add_contact(self, name: str, email: str, relationship: str = ""):
        """Add a frequently contacted person."""
        await self.store.put(
            self.namespace,
            f"contact:{email}",
            {"name": name, "email": email, "relationship": relationship}
        )

    async def search_contacts(self, query: str) -> list:
        """Search contacts by name or email."""
        items = await self.store.search(
            self.namespace,
            filter={"key": {"$prefix": "contact:"}},
            query=query
        )
        return [item.value for item in items]

    async def save_context(self, key: str, context: dict):
        """Save conversation context for future reference."""
        await self.store.put(
            self.namespace,
            f"context:{key}",
            context
        )


# Usage in agent
async def create_agent_with_memory(user_id: str, ...):
    store = PostgresStore.from_conn_string(db_connection_string)
    memory = VoiceAgentMemory(store, user_id)

    # Load user preferences into system prompt
    preferred_meeting_time = await memory.get_preference("meeting_time", "morning")
    email_signature = await memory.get_preference("email_signature", "")

    # ... create agent with these preferences
```

### 5.3 Agent Graph Definition (Alternative: Raw LangGraph)

```python
# agent/graph.py

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal

def create_agent_for_user(
    user_id: str,
    oauth_service: OAuthService,
    db_connection_string: str
) -> StateGraph:
    """
    Create a LangGraph agent configured for a specific user.
    Each user gets their own tools with their own OAuth tokens.
    """

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
    )

    # Create tools with user's credentials
    tools = create_user_tools(user_id, oauth_service)

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Define the agent node
    def agent_node(state: MessagesState):
        """Main agent that processes messages and decides actions."""

        system_message = {
            "role": "system",
            "content": """You are a helpful voice-activated AI assistant that manages Google Workspace.

Available tools:
- google_drive: List, search, upload, share files
- google_gmail: Read, send, search emails
- google_calendar: View agenda, create/update events
- google_sheets: Read, append, update spreadsheets
- google_docs: Create, read documents

Guidelines:
1. Be concise - responses may be spoken aloud
2. Confirm before destructive actions (delete, send)
3. After actions, summarize what you did
4. If something fails, explain why and suggest alternatives

Current date: {date}
User's timezone: {timezone}"""
        }

        messages = [system_message] + state["messages"]
        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}

    # Define routing logic
    def should_continue(state: MessagesState) -> Literal["tools", END]:
        """Decide whether to call tools or end."""
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    graph = StateGraph(MessagesState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")  # After tools, go back to agent

    # Compile with checkpointer for persistence
    checkpointer = PostgresSaver.from_conn_string(db_connection_string)

    return graph.compile(checkpointer=checkpointer)


def create_user_tools(user_id: str, oauth_service: OAuthService) -> list:
    """Create tools bound to a specific user's credentials."""

    cli_executor = CLIExecutor(oauth_service)

    return [
        GoogleDriveTool(user_id, cli_executor),
        GoogleGmailTool(user_id, cli_executor),
        GoogleCalendarTool(user_id, cli_executor),
        GoogleSheetsTool(user_id, cli_executor),
        GoogleDocsTool(user_id, cli_executor),
    ]
```

### 5.2 Tool Definitions (LangGraph Format)

```python
# agent/tools/google_calendar.py

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, List

class CreateEventInput(BaseModel):
    """Input for creating a calendar event."""
    summary: str = Field(description="Event title")
    start: str = Field(description="Start time (natural language, e.g., 'tomorrow at 3pm')")
    end: Optional[str] = Field(default=None, description="End time (optional)")
    attendees: Optional[List[str]] = Field(default=None, description="List of attendee emails")
    description: Optional[str] = Field(default=None, description="Event description")

class GoogleCalendarTool:
    """Google Calendar tool for LangGraph agent."""

    def __init__(self, user_id: str, cli_executor: CLIExecutor):
        self.user_id = user_id
        self.cli_executor = cli_executor

    def get_tools(self) -> list:
        """Return all calendar tools."""
        return [
            self._create_agenda_tool(),
            self._create_event_tool(),
            self._create_list_events_tool(),
        ]

    def _create_agenda_tool(self):
        @tool
        async def get_agenda() -> str:
            """Get today's calendar agenda with upcoming events."""
            result = await self.cli_executor.execute_google_command(
                self.user_id,
                "+agenda"
            )

            if result.success:
                return f"Today's agenda:\n{result.output}"
            else:
                return f"Failed to get agenda: {result.error}"

        return get_agenda

    def _create_event_tool(self):
        @tool
        async def create_event(
            summary: str,
            start: str,
            end: Optional[str] = None,
            attendees: Optional[List[str]] = None,
            description: Optional[str] = None
        ) -> str:
            """
            Create a new calendar event.

            Args:
                summary: Event title
                start: Start time (e.g., "tomorrow at 3pm", "2024-01-20 14:00")
                end: End time (optional, defaults to 1 hour after start)
                attendees: List of email addresses to invite
                description: Event description
            """
            cmd = f'+insert --summary "{summary}" --start "{start}"'

            if end:
                cmd += f' --end "{end}"'
            if attendees:
                cmd += f' --attendees "{",".join(attendees)}"'
            if description:
                cmd += f' --description "{description}"'

            result = await self.cli_executor.execute_google_command(
                self.user_id,
                cmd
            )

            if result.success:
                return f"Event '{summary}' created successfully!"
            else:
                return f"Failed to create event: {result.error}"

        return create_event

    def _create_list_events_tool(self):
        @tool
        async def list_events(
            time_min: Optional[str] = None,
            time_max: Optional[str] = None,
            max_results: int = 10
        ) -> str:
            """
            List calendar events within a time range.

            Args:
                time_min: Start of range (e.g., "today", "2024-01-20")
                time_max: End of range (optional)
                max_results: Maximum number of events to return
            """
            params = {"maxResults": max_results}
            if time_min:
                params["timeMin"] = time_min
            if time_max:
                params["timeMax"] = time_max

            result = await self.cli_executor.execute_google_command(
                self.user_id,
                f'calendar events list --params \'{json.dumps(params)}\''
            )

            if result.success:
                events = result.output.get("items", [])
                if not events:
                    return "No events found in that time range."

                response = f"Found {len(events)} events:\n"
                for event in events:
                    start = event.get("start", {}).get("dateTime", "All day")
                    response += f"- {event['summary']} ({start})\n"
                return response
            else:
                return f"Failed to list events: {result.error}"

        return list_events
```

---

## 6. Voice Processing Pipeline

### 6.1 Complete Voice Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           VOICE PROCESSING PIPELINE                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. RECORD  │────>│  2. UPLOAD  │────>│  3. STT     │────>│  4. AGENT   │
│  (Mobile)   │     │  (Mobile)   │     │  (Groq)     │     │  (LangGraph)│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐            │
│  7. PLAY    │<────│  6. DOWNLOAD│<────│  5. TTS     │<───────────┘
│  (Mobile)   │     │  (Mobile)   │     │  (Gemini)   │
└─────────────┘     └─────────────┘     └─────────────┘

Total latency target: < 2 seconds (excluding agent execution time)
```

### 6.2 Voice Service Implementation

```python
# services/voice_service.py

from groq import Groq
import google.generativeai as genai
from google.generativeai import types
import io

class VoiceService:
    """
    Handles Speech-to-Text (Groq Whisper) and Text-to-Speech (Gemini).
    """

    def __init__(self, groq_api_key: str, gemini_api_key: str):
        # Groq for STT
        self.groq_client = Groq(api_key=groq_api_key)

        # Gemini for TTS
        genai.configure(api_key=gemini_api_key)
        self.tts_model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")

    # ============================================
    # SPEECH-TO-TEXT (Groq Whisper)
    # ============================================

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        filename: str = "audio.wav"
    ) -> TranscriptionResult:
        """
        Convert speech to text using Groq Whisper.

        Performance:
        - Model: whisper-large-v3-turbo
        - Speed: 216x real-time (30s audio = ~140ms)
        - Cost: $0.04/hour

        Args:
            audio_data: Audio bytes (wav, mp3, m4a, etc.)
            language: ISO-639-1 language code
            filename: Original filename with extension

        Returns:
            TranscriptionResult with text and metadata
        """
        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename

            # Call Groq API
            transcription = self.groq_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                language=language,
                response_format="verbose_json",
                temperature=0.0,  # Most accurate
            )

            return TranscriptionResult(
                text=transcription.text,
                language=transcription.language,
                duration=transcription.duration,
                segments=transcription.segments,
                confidence=self._calculate_confidence(transcription.segments)
            )

        except Exception as e:
            raise VoiceProcessingError(f"STT failed: {str(e)}")

    def _calculate_confidence(self, segments: list) -> float:
        """Calculate average confidence from segment log probabilities."""
        if not segments:
            return 0.0

        avg_logprob = sum(s.get("avg_logprob", -1) for s in segments) / len(segments)
        # Convert log probability to 0-1 confidence
        return min(1.0, max(0.0, 1.0 + avg_logprob / 2))

    # ============================================
    # TEXT-TO-SPEECH (Gemini)
    # ============================================

    async def synthesize(
        self,
        text: str,
        voice: str = "Kore",
        style: str = None
    ) -> bytes:
        """
        Convert text to speech using Gemini TTS.

        Args:
            text: Text to speak
            voice: Voice name (Kore, Puck, Charon, etc.)
            style: Optional style instruction (e.g., "cheerfully", "professionally")

        Returns:
            Audio bytes (WAV format)
        """
        try:
            # Construct prompt with optional style
            if style:
                content = f"Say {style}: {text}"
            else:
                content = text

            # Call Gemini TTS
            response = self.tts_model.generate_content(
                content,
                generation_config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        )
                    )
                )
            )

            # Extract audio data
            audio_data = response.candidates[0].content.parts[0].inline_data.data

            return audio_data

        except Exception as e:
            raise VoiceProcessingError(f"TTS failed: {str(e)}")

    # Available voices for reference
    VOICES = [
        "Aoede", "Charon", "Fenrir", "Kore", "Puck", "Zephyr",
        "Leda", "Orus", "Perseus", "Vesta", "Calliope", "Autonoe",
        "Enceladus", "Iapetus", "Umbriel", "Algieba", "Despina",
        "Erinome", "Gacrux", "Laomedeia", "Pulcherrima", "Achird",
        "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager",
        "Sulafat", "Lesath", "Alnilam", "Schedar"
    ]


@dataclass
class TranscriptionResult:
    text: str
    language: str
    duration: float
    segments: list
    confidence: float


class VoiceProcessingError(Exception):
    pass
```

### 6.3 Voice API Endpoints

```python
# api/voice.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import Response

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

@router.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = "en",
    user: User = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Convert audio to text using Groq Whisper.

    Accepts: wav, mp3, m4a, flac, ogg, webm
    Max size: 25MB
    """
    # Validate file size
    content = await audio.read()
    if len(content) > 25 * 1024 * 1024:  # 25MB
        raise HTTPException(400, "File too large (max 25MB)")

    # Transcribe
    result = await voice_service.transcribe(
        audio_data=content,
        language=language,
        filename=audio.filename
    )

    return {
        "text": result.text,
        "language": result.language,
        "duration": result.duration,
        "confidence": result.confidence
    }


@router.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    user: User = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Convert text to speech using Gemini TTS.

    Returns: audio/wav
    """
    audio_data = await voice_service.synthesize(
        text=request.text,
        voice=request.voice or "Kore",
        style=request.style
    )

    return Response(
        content=audio_data,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"attachment; filename=speech.wav"
        }
    )


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "Kore"
    style: Optional[str] = None
```

---

## 7. Onboarding Flow

### 7.1 Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ONBOARDING FLOW                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. SPLASH  │────>│ 2. WELCOME  │────>│ 3. PERMS    │────>│ 4. CONNECT  │
│             │     │             │     │             │     │             │
│  App icon   │     │  "Voice     │     │  Request:   │     │  Connect    │
│  loading    │     │   Agent"    │     │  - Mic      │     │  Google     │
│             │     │  intro      │     │  - Notifs   │     │  Account    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐            │
│  7. CHAT    │<────│ 6. READY    │<────│ 5. SUCCESS  │<───────────┘
│             │     │             │     │             │
│  Main app   │     │  "You're    │     │  "Google    │
│  interface  │     │   ready!"   │     │   linked!"  │
│             │     │  tutorial   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 7.2 Onboarding Screens Implementation

```typescript
// screens/onboarding/OnboardingFlow.tsx

const OnboardingFlow: React.FC = () => {
  const [step, setStep] = useState<OnboardingStep>('welcome');
  const navigation = useNavigation();

  const handleComplete = async () => {
    await AsyncStorage.setItem('onboarding_complete', 'true');
    navigation.reset({
      index: 0,
      routes: [{ name: 'Main' }],
    });
  };

  return (
    <View style={styles.container}>
      {step === 'welcome' && (
        <WelcomeScreen onNext={() => setStep('permissions')} />
      )}
      {step === 'permissions' && (
        <PermissionsScreen onNext={() => setStep('connect')} />
      )}
      {step === 'connect' && (
        <ConnectAccountScreen onNext={() => setStep('ready')} />
      )}
      {step === 'ready' && (
        <ReadyScreen onComplete={handleComplete} />
      )}
    </View>
  );
};

// ============================================
// WELCOME SCREEN
// ============================================

const WelcomeScreen: React.FC<{ onNext: () => void }> = ({ onNext }) => (
  <SafeAreaView style={styles.screen}>
    <View style={styles.content}>
      <LottieAnimation source={require('../assets/voice-wave.json')} />

      <Text style={styles.title}>Voice Agent</Text>
      <Text style={styles.subtitle}>
        Your AI assistant for Google Workspace
      </Text>

      <View style={styles.features}>
        <FeatureItem
          icon={<CalendarIcon />}
          text="Manage your calendar with voice"
        />
        <FeatureItem
          icon={<MailIcon />}
          text="Send and read emails hands-free"
        />
        <FeatureItem
          icon={<FolderIcon />}
          text="Search and organize files"
        />
      </View>
    </View>

    <Button
      title="Get Started"
      onPress={onNext}
      style={styles.primaryButton}
    />
  </SafeAreaView>
);

// ============================================
// PERMISSIONS SCREEN
// ============================================

const PermissionsScreen: React.FC<{ onNext: () => void }> = ({ onNext }) => {
  const [micGranted, setMicGranted] = useState(false);
  const [notifGranted, setNotifGranted] = useState(false);

  const requestMicrophone = async () => {
    const { status } = await Audio.requestPermissionsAsync();
    setMicGranted(status === 'granted');
  };

  const requestNotifications = async () => {
    const { status } = await Notifications.requestPermissionsAsync();
    setNotifGranted(status === 'granted');
  };

  const canProceed = micGranted; // Mic is required, notifs optional

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.content}>
        <Text style={styles.title}>Permissions</Text>
        <Text style={styles.subtitle}>
          Voice Agent needs a few permissions to work
        </Text>

        <PermissionItem
          icon={<MicIcon />}
          title="Microphone"
          description="Required for voice commands"
          granted={micGranted}
          onRequest={requestMicrophone}
          required
        />

        <PermissionItem
          icon={<BellIcon />}
          title="Notifications"
          description="Get notified when tasks complete"
          granted={notifGranted}
          onRequest={requestNotifications}
        />
      </View>

      <Button
        title="Continue"
        onPress={onNext}
        disabled={!canProceed}
        style={styles.primaryButton}
      />
    </SafeAreaView>
  );
};

// ============================================
// CONNECT ACCOUNT SCREEN
// ============================================

const ConnectAccountScreen: React.FC<{ onNext: () => void }> = ({ onNext }) => {
  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(false);
  const { connectGoogle } = useAuth();

  const handleConnect = async () => {
    setConnecting(true);
    try {
      await connectGoogle();
      setConnected(true);
      // Auto-proceed after short delay
      setTimeout(onNext, 1500);
    } catch (error) {
      Alert.alert('Error', 'Failed to connect Google account');
    } finally {
      setConnecting(false);
    }
  };

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.content}>
        <Text style={styles.title}>Connect Google</Text>
        <Text style={styles.subtitle}>
          Link your Google Workspace to get started
        </Text>

        <View style={styles.accountCard}>
          <GoogleIcon size={48} />
          <Text style={styles.accountName}>Google Workspace</Text>
          <Text style={styles.accountDesc}>
            Gmail, Calendar, Drive, Docs, Sheets
          </Text>

          {connected ? (
            <View style={styles.connectedBadge}>
              <CheckIcon color="green" />
              <Text style={styles.connectedText}>Connected!</Text>
            </View>
          ) : (
            <Button
              title={connecting ? "Connecting..." : "Connect Google"}
              onPress={handleConnect}
              loading={connecting}
              icon={<GoogleIcon />}
            />
          )}
        </View>

        <Text style={styles.privacyNote}>
          We only access what you explicitly allow.
          You can disconnect anytime in Settings.
        </Text>
      </View>

      {!connected && (
        <TouchableOpacity onPress={onNext} style={styles.skipButton}>
          <Text style={styles.skipText}>Skip for now</Text>
        </TouchableOpacity>
      )}
    </SafeAreaView>
  );
};

// ============================================
// READY SCREEN
// ============================================

const ReadyScreen: React.FC<{ onComplete: () => void }> = ({ onComplete }) => (
  <SafeAreaView style={styles.screen}>
    <View style={styles.content}>
      <LottieAnimation source={require('../assets/success.json')} autoPlay />

      <Text style={styles.title}>You're all set!</Text>
      <Text style={styles.subtitle}>
        Try these voice commands:
      </Text>

      <View style={styles.exampleCommands}>
        <ExampleCommand text='"What\'s on my calendar today?"' />
        <ExampleCommand text='"Send an email to John about the meeting"' />
        <ExampleCommand text='"Find my budget spreadsheet"' />
      </View>

      <View style={styles.tip}>
        <LightbulbIcon />
        <Text style={styles.tipText}>
          Tap and hold the microphone button to speak
        </Text>
      </View>
    </View>

    <Button
      title="Start Using Voice Agent"
      onPress={onComplete}
      style={styles.primaryButton}
    />
  </SafeAreaView>
);
```

---

## 8. Token Refresh Strategy

### 8.1 Proactive Token Refresh

```python
# services/token_refresh_service.py

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

class TokenRefreshService:
    """
    Proactively refreshes OAuth tokens before they expire.
    Runs as a background task.
    """

    REFRESH_BUFFER = timedelta(minutes=10)  # Refresh 10 min before expiry
    CHECK_INTERVAL = timedelta(minutes=5)   # Check every 5 minutes

    def __init__(self, db_session_factory, oauth_service: OAuthService):
        self.db_session_factory = db_session_factory
        self.oauth_service = oauth_service
        self._running = False

    async def start(self):
        """Start the background refresh loop."""
        self._running = True

        while self._running:
            await self._refresh_expiring_tokens()
            await asyncio.sleep(self.CHECK_INTERVAL.total_seconds())

    def stop(self):
        """Stop the background refresh loop."""
        self._running = False

    async def _refresh_expiring_tokens(self):
        """Find and refresh tokens that are about to expire."""

        async with self.db_session_factory() as db:
            # Find tokens expiring within buffer time
            expiry_threshold = datetime.utcnow() + self.REFRESH_BUFFER

            expiring_tokens = await db.execute(
                select(OAuthCredential).where(
                    OAuthCredential.token_expiry < expiry_threshold,
                    OAuthCredential.token_expiry > datetime.utcnow()
                )
            )

            for cred in expiring_tokens.scalars():
                try:
                    if cred.provider == 'google':
                        await self.oauth_service._refresh_google_token(
                            cred.user_id, cred
                        )
                    elif cred.provider == 'microsoft':
                        await self.oauth_service._refresh_microsoft_token(
                            cred.user_id, cred
                        )

                    print(f"Refreshed {cred.provider} token for user {cred.user_id}")

                except Exception as e:
                    print(f"Failed to refresh token: {e}")
                    # Could notify user that re-auth is needed


# Start in FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start token refresh service
    refresh_service = TokenRefreshService(
        db_session_factory=get_async_session,
        oauth_service=oauth_service
    )
    refresh_task = asyncio.create_task(refresh_service.start())

    yield

    # Cleanup
    refresh_service.stop()
    refresh_task.cancel()
```

---

## 9. Complete Technology Stack

### 9.1 Final Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Mobile App** | | |
| Framework | React Native + Expo | Cross-platform iOS/Android |
| UI | assistant-ui (LangGraph runtime) | Claude-like chat interface |
| State | Zustand | Lightweight state management |
| Voice Recording | expo-av | Audio capture |
| Secure Storage | expo-secure-store | JWT token storage |
| Navigation | React Navigation (Drawer) | Thread management |
| **Backend** | | |
| API | FastAPI | Async Python API + WebSocket |
| AI Agent | LangGraph | Stateful agent with tools |
| LLM | Gemini 2.0 Flash | Intent understanding & responses |
| STT | Groq Whisper (whisper-large-v3-turbo) | Speech-to-text |
| TTS | Gemini 2.5 Flash TTS | Text-to-speech |
| Database | PostgreSQL | Users, OAuth, checkpoints |
| Cache | Redis | Sessions, rate limiting |
| CLI | Google Workspace CLI (gws) | Workspace automation |
| **Infrastructure** | | |
| Cloud | Google Cloud Platform | Native Gemini integration |
| Compute | Cloud Run | Serverless containers |
| Database | Cloud SQL (PostgreSQL) | Managed database |
| Cache | Memorystore (Redis) | Managed Redis |
| Secrets | Secret Manager | API keys, encryption keys |

### 9.2 Quick Start Commands

```bash
# Mobile App
npx assistant-ui@latest create -t langgraph
cd my-app
npm install expo-av expo-secure-store zustand

# Backend
pip install fastapi langgraph langchain-google-genai groq psycopg2-binary redis

# Google Workspace CLI (in Docker)
npm install -g @anthropic-ai/gws
```

---

## 10. References

### Documentation Links

| Resource | URL |
|----------|-----|
| **DeepAgents** | https://docs.langchain.com/oss/python/deepagents/overview |
| **Groq Whisper STT** | https://console.groq.com/docs/speech-to-text |
| **Gemini TTS** | https://ai.google.dev/gemini-api/docs/speech-generation |
| **Google Workspace CLI** | https://github.com/googleworkspace/cli |
| **Microsoft 365 CLI** | https://pnp.github.io/cli-microsoft365/ |
| **assistant-ui** | https://www.assistant-ui.com/ |
| **assistant-ui Docs** | https://www.assistant-ui.com/docs |
| **assistant-ui React Native** | https://www.assistant-ui.com/docs/react-native |
| **assistant-ui LangGraph Runtime** | https://www.assistant-ui.com/docs/runtimes/langgraph |
| **assistant-ui Examples** | https://www.assistant-ui.com/examples |
| **assistant-ui Claude Example** | https://www.assistant-ui.com/examples/claude |
| **assistant-ui Primitives** | https://www.assistant-ui.com/docs/primitives |
| **LangGraph Overview** | https://docs.langchain.com/oss/python/langgraph/overview |
| **LangGraph Workflows & Agents** | https://docs.langchain.com/oss/python/langgraph/workflows-agents |
| **LangChain** | https://docs.langchain.com/oss/python/langchain/overview |
| **React Native Expo** | https://expo.dev/ |
| **expo-av (Audio)** | https://docs.expo.dev/versions/latest/sdk/av/ |
| **expo-secure-store** | https://docs.expo.dev/versions/latest/sdk/securestore/ |
| **expo-auth-session** | https://docs.expo.dev/versions/latest/sdk/auth-session/ |
| **Zustand** | https://github.com/pmndrs/zustand |
| **FastAPI** | https://fastapi.tiangolo.com/ |
| **FastAPI WebSocket** | https://fastapi.tiangolo.com/advanced/websockets/ |
| **Google OAuth 2.0** | https://developers.google.com/identity/protocols/oauth2 |
| **Microsoft OAuth 2.0** | https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow |

### API Pricing

| Service | Cost |
|---------|------|
| Groq Whisper (turbo) | $0.04/hour of audio |
| Groq Whisper (large-v3) | $0.111/hour of audio |
| Gemini 2.0 Flash | $0.075/1M input tokens, $0.30/1M output |
| Gemini TTS | Included with API (check current pricing) |
| Google Workspace API | Free (with user OAuth) |
| Microsoft Graph API | Free (with user OAuth) |

### Quick Start Commands

```bash
# Mobile App (using assistant-ui LangGraph template)
npx assistant-ui@latest create -t langgraph my-voice-agent
cd my-voice-agent
npm install expo-av expo-secure-store expo-auth-session zustand

# Backend
pip install fastapi uvicorn langgraph langchain-google-genai groq psycopg2-binary redis cryptography

# Google Workspace CLI
npm install -g @anthropic-ai/gws

# Run backend
uvicorn app.main:app --reload

# Run mobile app
npx expo start
```

---

## 11. Next Steps

### Immediate (Week 1)
1. [ ] Set up Expo project with assistant-ui LangGraph template
2. [ ] Set up FastAPI backend with **DeepAgents**
3. [ ] Implement Google OAuth flow (mobile + backend)
4. [ ] Test Groq Whisper STT integration

### Short-term (Week 2-3)
5. [ ] Implement CLI executor with token injection (multi-user)
6. [ ] Create first tool (Google Calendar) with DeepAgent
7. [ ] Connect mobile ↔ backend via WebSocket
8. [ ] Implement push-to-talk voice flow
9. [ ] Add Gemini TTS for voice responses

### Medium-term (Week 4-6)
10. [ ] Add remaining Google tools (Drive, Gmail, Sheets, Docs)
11. [ ] Implement DeepAgent memory (user preferences)
12. [ ] Complete onboarding flow
13. [ ] Polish UI and voice feedback
14. [ ] Testing and bug fixes

### Future (v2)
15. [ ] Add Microsoft 365 integration
16. [ ] Add always-listening wake word (Android first)
17. [ ] Web app version

---

*Document Version: 2.0*
*Architecture Status: FINALIZED*
*Ready for Implementation: YES*
