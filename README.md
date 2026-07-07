# Voice AI Workspace Agent

A mobile-first voice AI workspace agent for Google Workspace and Microsoft 365, built around DeepAgents for orchestration and Composio for external integrations.

This repo now contains a real full-stack scaffold:
- `apps/server`: FastAPI backend
- `apps/mobile`: Expo React Native mobile app
- `docs`: architecture, LLD, UI system, and environment contract

## Product Direction

- Voice-first UX with text fallback
- Wake-word assistant target with hold-to-talk fallback
- Clean chat interface with explicit approval states
- Composio-managed Google Workspace and Microsoft 365 integrations
- DeepAgents as the agent runtime
- Reliable execution with audit logs, retries, and graceful degradation

## Reliability Posture

The system should be engineered for production-grade reliability, but no honest architecture can promise literal 100% uptime or success across mobile devices, networks, and third-party APIs.

This design targets:
- strong observability
- safe write approvals
- graceful degradation
- no silent failure
- clean recovery paths

## Current Docs

- [Architecture v4](/Users/mugilansakthivel/Developer/voice/docs/ARCHITECTURE-v2.md)
- [LLD](/Users/mugilansakthivel/Developer/voice/docs/LLD-Voice-AI-Agent.md)
- [UI System](/Users/mugilansakthivel/Developer/voice/docs/UI-SYSTEM.md)
- [Environment Variables](/Users/mugilansakthivel/Developer/voice/docs/ENVIRONMENT.md)
- [LLD Critique](/Users/mugilansakthivel/Developer/voice/docs/LLD-CRITIQUE.md)

## Project Structure

```text
apps/
  mobile/   Expo app with clean assistant-style UI
  server/   FastAPI API, approvals, voice routes, Composio and Supabase services
docs/
  architecture, LLD, UI, env contract
```

## Finalized Stack

### Mobile
- React Native + Expo
- assistant-ui
- Zustand

### Backend
- FastAPI
- DeepAgents
- Supabase Postgres
- Object storage

### Integrations
- Composio for Google Workspace and Microsoft 365 actions
- Composio CLI for local QA and tool discovery

### Voice and Model Providers
- one primary LLM provider
- one primary STT provider
- one primary TTS provider

These are intentionally configurable through environment variables instead of being hard-coded in the architecture.

## What Is Implemented

### Backend
- health endpoint
- chat endpoint
- websocket stub
- voice STT/TTS endpoints
- Composio connection endpoints
- approval confirm/reject flow
- Supabase and Composio service wrappers

### Mobile
- clean chat shell
- assistant-ui runtime wrapper
- voice status display
- approval card flow
- API client wiring

Current reality:
- the checked-in mobile scaffold still behaves like a chat-first / hold-to-talk shell
- the new LLD now defines the target wake-word, background-listening, and follow-up conversation architecture
- native audio and wake-word work still needs to be built in a development build, not Expo Go

The current backend is scaffolded to run in a safe dry-run mode when Composio or provider keys are missing.

## Environment Setup

The full environment contract is documented in [ENVIRONMENT.md](/Users/mugilansakthivel/Developer/voice/docs/ENVIRONMENT.md), and a starter file exists at [.env.example](/Users/mugilansakthivel/Developer/voice/.env.example).

The minimum values needed to start implementation are:
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ENCRYPTION_KEY`
- `COMPOSIO_API_KEY`
- `COMPOSIO_WEBHOOK_SECRET`
- one LLM provider and model
- one STT provider and model
- one TTS provider, model, and voice
- `EXPO_PUBLIC_API_URL`
- `EXPO_PUBLIC_WS_URL`

## Run Locally

### Backend

```bash
cd apps/server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Mobile

```bash
cd apps/mobile
npm install
npm run start
```

## Recommended Build Order

1. Backend skeleton with auth, threads, approvals, and Composio account linking.
2. Mobile shell with clean chat UI, approvals, and integrations screen.
3. Google Calendar and Gmail flows.
4. Real voice pipeline with STT, TTS, and short spoken results.
5. Wake word, VAD, follow-up listening, and background listening mode.
6. Outlook, Calendar, Drive, Docs, Sheets, Teams, OneDrive, and To Do expansion.

## Next Step

The scaffold is ready. The next useful input from you is the real environment values for Supabase, Composio, and the voice/model providers you want first, so I can replace the dry-run service behavior with live integrations.
