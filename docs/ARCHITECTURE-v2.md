# Voice AI Workspace Agent - Architecture v4

## Document Info
- Version: 4.0
- Date: 2026-03-30
- Status: Build-ready architecture baseline
- Primary Goal: Reliable voice-first workspace agent

---

## 1. Architecture Goals

We are designing this product to feel voice-native, fast, and dependable.

The product goals are:
- users should be able to complete supported tasks fully by voice
- the UI should stay clean and calm even during complex tool workflows
- risky actions should be explicit and auditable
- failures should degrade gracefully instead of confusing the user

Important reality:
- no mobile app, API platform, or third-party provider can honestly guarantee literal 100% uptime or success
- the architecture should instead target high reliability, fast recovery, strong observability, and zero silent failure

### 1.1 Reliability Targets

| Area | Target |
|------|--------|
| API availability | 99.9%+ service target |
| Voice interaction mode | Wake-word target with foreground fallback, phased background listening |
| Read-only request latency | p95 under 4 seconds for simple requests |
| Write action safety | 100% approval coverage for risky side effects |
| Error visibility | 0 silent failures |
| Tool traceability | 100% action logs with request IDs |

### 1.2 Product Decisions

| Area | Decision |
|------|----------|
| Agent framework | DeepAgents |
| Integration layer | Composio |
| Platform | Mobile only in v1 |
| Voice input | Wake word plus hold-to-talk fallback |
| Voice output | TTS with text fallback |
| Chat UI | assistant-ui with a custom clean visual system |
| Backend | FastAPI services |
| Primary stores | Supabase Postgres + object storage |
| Deployment model | Stateless API + worker tier |

---

## 2. System Overview

```text
+----------------------------------------------------------------------------------+
|                           MOBILE APP (React Native + Expo)                       |
|                                                                                  |
|  Voice capture | assistant-ui thread | approval sheets | playback | auth store   |
+----------------------------------------------+-----------------------------------+
                                               |
                                               | HTTPS / WebSocket
                                               v
+----------------------------------------------------------------------------------+
|                         API LAYER (FastAPI, stateless)                           |
|                                                                                  |
|  Auth | Chat | Voice STT | Voice TTS | Threads | Approvals | Integration APIs    |
+----------------------------------------------+-----------------------------------+
                                               |
                                               v
+----------------------------------------------------------------------------------+
|                        AGENT ORCHESTRATION (DeepAgents)                          |
|                                                                                  |
|  intent_router -> planner -> account_guard -> approval_guard -> executor         |
|                        -> summarizer -> response_streamer                        |
+----------------------------------------------+-----------------------------------+
                                               |
                                               v
+----------------------------------------------------------------------------------+
|                     WORKSPACE ACTION BROKER + COMPOSIO CLIENT                    |
|                                                                                  |
|  tool discovery | account resolution | execution | retries | normalization       |
+--------------------------+-----------------------------------+--------------------+
                           |                                   |
                           v                                   v
+---------------------------------------+      +-----------------------------------+
|   DATA + STATE                         |      |   OBSERVABILITY                   |
|   Supabase Postgres                    |      |   logs                            |
|   Postgres-backed state tables         |      |   metrics                         |
|   Object storage                       |      |   traces                          |
|   checkpoints / approvals / logs       |      |   alerts                          |
+---------------------------------------+      +-----------------------------------+
                           |
                           v
+----------------------------------------------------------------------------------+
|                     GOOGLE WORKSPACE + MICROSOFT 365 VIA COMPOSIO                |
+----------------------------------------------------------------------------------+
```

---

## 3. Reliability Principles

### 3.1 Voice-First, Not Voice-Only
Voice is the primary experience, but we still need safe fallback paths:
- if STT fails, the user can retry immediately
- if TTS fails, the text response still appears in the thread
- if a tool call fails, the agent explains what happened and what was not done

### 3.2 No Silent Failure
Every failure must become one of these:
- a user-visible message
- a retryable background event
- a logged operational alert

### 3.3 Safe Writes
The agent must not send email, create meetings, share files, or post messages without either:
- clear prior user intent and policy coverage, or
- an explicit approval step

### 3.4 Graceful Degradation
If one subsystem is unhealthy:
- voice can degrade to text
- write actions can pause while read-only actions continue
- Composio/provider outages should not break thread history or session state

### 3.5 Observable by Default
Every request gets:
- a request ID
- a thread ID
- a user ID
- a tool execution log
- a provider execution ID when available

---

## 4. Voice Architecture

### 4.1 Voice Flow

```text
passive wake word -> beep -> capture post-wake command -> STT -> DeepAgents
                  -> tool execution -> response text -> TTS -> playback
                  -> 5-second follow-up window -> passive wake word
```

### 4.2 Voice Interaction Strategy
The product target is wake-word interaction, but the architecture must stay honest about platform limits.

That means:
- foreground voice must always work
- wake word should be on-device
- Android can support stronger background listening than iOS
- hold-to-talk remains the fallback path when background listening is unavailable or disabled

Design implications:
- event-driven acknowledgments instead of timer spam
- short follow-up conversation window after each spoken result
- explicit stop and cancel behavior
- background listening only when the user has armed it

### 4.3 Voice Reliability Rules
- maximum recording length per turn
- transcription timeout with user-visible retry
- transcript confidence threshold for clarification
- audio upload checksum validation
- no overlapping TTS playback and recording unless barge-in interrupts playback
- stop playback immediately when the user starts speaking
- follow-up listening expires quickly and silently returns to passive mode
- background listening must always be visibly indicated to the user

### 4.4 Latency Budget

| Stage | Target |
|------|--------|
| Upload + STT | under 1.5s for short commands |
| Agent planning | under 1.0s for simple reads |
| Tool execution | under 2.0s for simple operations |
| TTS start | under 1.0s after final text |

These are design targets, not promises.

---

## 5. Agent Architecture

### 5.1 DeepAgents Responsibilities
- parse intent from voice or text
- plan the smallest safe sequence of actions
- check user account connectivity
- decide whether approval is required
- call workspace tools through the broker
- summarize outcomes in natural language

### 5.2 Agent Graph

```text
intent_router
  -> account_guard
  -> planner
  -> approval_guard
  -> executor
  -> summarizer
  -> response_streamer
```

### 5.3 Stable Tool Surface
The agent should use a small stable internal tool contract, for example:
- `google_calendar.create_event`
- `google_gmail.send_email`
- `google_drive.search_files`
- `microsoft_outlook.send_email`
- `microsoft_teams.create_meeting`
- `microsoft_onedrive.list_files`

This keeps the agent prompt and reasoning stable even if Composio action names evolve.

### 5.4 Approval Policy
Approval is required for:
- sending emails
- creating meetings with attendees
- posting messages in shared spaces
- sharing files externally
- deleting or editing data

Approval is usually skipped for:
- listing files
- reading calendars
- draft generation
- search operations

---

## 6. Integration Architecture

### 6.1 Composio-First Model
We are standardizing all workspace integrations through Composio.

That means:
- no direct `gws` runtime dependency
- no direct `m365` runtime dependency
- no provider-specific OAuth token storage in our backend for v1
- one broker pattern for Google and Microsoft capabilities

### 6.2 Integration Layers

#### Workspace Action Broker
- resolves the best account for a request
- maps internal tool names to Composio actions
- applies timeout, retry, and approval rules
- normalizes results and errors

#### Composio Client
- production path uses Composio API or SDK
- CLI remains available for local QA and manual smoke tests

### 6.3 Connected Account Model
Each user may have:
- zero or more Google connected accounts
- zero or more Microsoft connected accounts
- different scopes per app or integration

The backend stores connection references and metadata, not raw provider refresh tokens.

### 6.4 Webhooks
If Composio execution or account lifecycle events are asynchronous, the backend exposes a webhook endpoint to:
- receive completion events
- receive disconnect or auth expiry signals
- update connection status
- resume paused workflows

---

## 7. Data and State

### 7.1 Core Tables
- `users`
- `sessions`
- `threads`
- `messages`
- `connected_accounts`
- `tool_executions`
- `approvals`
- `agent_checkpoints`

### 7.2 Transient State Without Redis
- use Postgres tables for approvals, idempotency, and durable workflow state
- keep websocket fan-out logic inside the active API process in v1
- add an external cache later only if scale proves it necessary

### 7.3 Object Storage
- voice uploads
- generated audio responses
- optional attachments
- temporary export artifacts

### 7.4 Retention
- raw audio should have configurable retention
- transcripts and action logs should be retained longer than media blobs
- PII-heavy artifacts should be deletable per user request

---

## 8. Deployment Topology

### 8.1 Runtime Components

```text
Load Balancer
  -> API service replicas
  -> WebSocket-capable chat service
  -> background worker service
  -> webhook receiver
  -> Supabase Postgres
  -> object storage
  -> monitoring stack
```

### 8.2 Services

#### API Service
- stateless
- handles auth, chat, approvals, STT/TTS request routing, thread reads

#### Worker Service
- executes longer tool flows
- handles retries
- processes webhook follow-up tasks

#### Webhook Receiver
- validates Composio signatures
- updates account state and execution state

### 8.3 Scaling Rules
- API scales on CPU, memory, and request concurrency
- WebSocket capacity is tracked separately from standard HTTP throughput
- workers scale on queue depth and tool execution duration

---

## 9. Clean UI System

The interface should feel premium, calm, and obvious under stress.

The concrete UI design system is documented in [UI-SYSTEM.md](/Users/mugilansakthivel/Developer/voice/docs/UI-SYSTEM.md) and should be implemented on top of `assistant-ui`, not beside it.

### 9.1 Design Principles
- one clear primary action per screen
- large touch targets
- strong hierarchy
- minimal decorative noise
- status always visible
- approvals impossible to misunderstand

### 9.2 Core Screens
- conversation screen
- integration connection screen
- approval sheet
- voice capture state
- settings and account management

### 9.3 Conversation Screen Layout
- compact header with workspace status
- large readable thread
- clean composer
- prominent hold-to-talk control
- expandable tool cards for action details

### 9.4 Voice States
The voice UI should show these states clearly:
- idle
- listening
- transcribing
- thinking
- waiting for approval
- speaking
- failed

### 9.5 Visual Direction
- warm neutral background, not sterile white
- high contrast typography
- restrained accent color for confirmations and interactive states
- monospace only for technical details, never for primary conversation text
- subtle motion only where it helps comprehension

### 9.6 Accessibility
- dynamic text support
- captions for spoken responses
- haptics for voice start/stop
- color is never the only state indicator

---

## 10. Observability and Operations

### 10.1 Logs
Structured logs for:
- request lifecycle
- STT and TTS timings
- tool execution lifecycle
- approval lifecycle
- reconnect and account failures

### 10.2 Metrics
- request success rate
- STT error rate
- TTS error rate
- tool success rate by app and action
- approval completion rate
- websocket disconnect rate
- p50, p95, p99 latency by step

### 10.3 Alerts
- Composio execution failure spike
- webhook signature validation failures
- STT/TTS provider outage
- queue backlog growth
- database connection saturation

### 10.4 Replayability
For support and debugging, we should be able to reconstruct:
- what the user asked
- what the agent planned
- what tools were proposed
- whether approval was given
- what Composio returned

---

## 11. Security Model

### 11.1 Security Requirements
- JWT-based app auth
- encrypted secrets at rest
- signed webhook validation
- RBAC for admin/operator actions
- audit trail for all external actions

### 11.2 Sensitive Data Handling
- redact secrets from logs
- never echo provider credentials into client responses
- store only required account metadata
- allow user disconnect and data cleanup workflows

### 11.3 Idempotency
Every write-capable tool call should include or map to an idempotency strategy where supported to reduce duplicate side effects.

---

## 12. Environment Model

The required environment variables are documented in [ENVIRONMENT.md](/Users/mugilansakthivel/Developer/voice/docs/ENVIRONMENT.md) and mirrored in [.env.example](/Users/mugilansakthivel/Developer/voice/.env.example).

At a minimum, implementation needs values for:
- app auth and encryption
- Supabase database and project access
- Composio
- one LLM provider
- one STT provider
- one TTS provider
- storage
- observability

---

## 13. Build Order

### Phase 1
- backend skeleton
- auth/session foundation
- thread and websocket foundation
- Composio account linking
- Google Calendar and Gmail happy paths
- clean conversation UI shell

### Phase 2
- voice pipeline
- approval flows
- audit logs
- Drive, Docs, Sheets
- Outlook and Calendar

### Phase 3
- Teams, OneDrive, Microsoft To Do
- retry queues
- reconnect flows
- admin tooling
- production observability

---

## 14. Ready-to-Build Summary

This architecture is ready for implementation because it now:
- centers reliability instead of optimistic demos
- treats voice as the primary UX without pretending background wake word is solved
- standardizes workspace execution through Composio
- gives DeepAgents a stable tool surface
- defines a clean UI direction instead of only naming a component library
- makes environment requirements explicit
