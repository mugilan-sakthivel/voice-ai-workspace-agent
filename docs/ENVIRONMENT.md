# Environment Variables

This project is designed so we can start implementation once these values are available.

## 1. Required To Start Building

These are the minimum values I need from you to wire the backend and mobile app with real services.

### 1.1 Core Backend

| Variable | Required | Purpose |
|----------|----------|---------|
| `APP_ENV` | Yes | `development`, `staging`, or `production` |
| `APP_BASE_URL` | Yes | Public backend URL |
| `WEB_BASE_URL` | Optional | Web dashboard URL if added later |
| `ENCRYPTION_KEY` | Yes | App-level encryption for sensitive metadata |
| `CORS_ALLOWED_ORIGINS` | Yes | Allowed client origins |

### 1.2 Supabase and Database

| Variable | Required | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | Yes | Supabase PostgreSQL connection string |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_ANON_KEY` or `SUPABASE_PUBLISHABLE_KEY` | Yes | Client-safe project key |
| `SUPABASE_SERVICE_ROLE_KEY` or `SUPABASE_SECRET_KEY` | Yes | Backend-only privileged key |
| `SUPABASE_DB_SCHEMA` | Optional | Default schema if not `public` |

### 1.3 Composio

| Variable | Required | Purpose |
|----------|----------|---------|
| `COMPOSIO_API_KEY` | Yes | Primary Composio backend access |
| `COMPOSIO_WEBHOOK_SECRET` | Yes | Verify incoming Composio webhooks |
| `COMPOSIO_BASE_URL` | Optional | Override base URL if needed |
| `COMPOSIO_DEFAULT_ENTITY_PREFIX` | Optional | Entity naming convention |
| `COMPOSIO_GOOGLE_AUTH_CONFIG_ID` | Recommended for Google connect flow | Composio auth config for Google Workspace |
| `COMPOSIO_GMAIL_AUTH_CONFIG_ID` | Recommended for Gmail | Toolkit-specific Composio auth config |
| `COMPOSIO_GOOGLECALENDAR_AUTH_CONFIG_ID` | Recommended for Google Calendar | Toolkit-specific Composio auth config |
| `COMPOSIO_MICROSOFT_AUTH_CONFIG_ID` | Recommended for Microsoft connect flow | Composio auth config for Microsoft 365 |

### 1.4 Agent Model

Pick one primary LLM provider for the first implementation.

| Variable | Required | Purpose |
|----------|----------|---------|
| `LLM_PROVIDER` | Yes | Example: `openai` or `google` |
| `LLM_MODEL` | Yes | Primary reasoning model name |
| `OPENAI_API_KEY` | Required if using OpenAI | Agent model access |
| `GOOGLE_API_KEY` | Required if using Google | Agent model access |

### 1.5 Speech-To-Text

Pick one STT provider for the first implementation.

| Variable | Required | Purpose |
|----------|----------|---------|
| `STT_PROVIDER` | Yes | Example: `groq`, `deepgram`, `openai` |
| `STT_MODEL` | Yes | STT model identifier |
| `GROQ_API_KEY` | Required if using Groq | STT access |
| `DEEPGRAM_API_KEY` | Required if using Deepgram | STT access |
| `OPENAI_API_KEY` | Required if using OpenAI STT | STT access |

### 1.6 Text-To-Speech

Pick one TTS provider for the first implementation.

| Variable | Required | Purpose |
|----------|----------|---------|
| `TTS_PROVIDER` | Yes | Example: `google`, `openai`, `elevenlabs` |
| `TTS_MODEL` | Yes | TTS model identifier |
| `TTS_VOICE` | Yes | Default voice name |
| `GOOGLE_API_KEY` | Required if using Google TTS via Gemini API | TTS access |
| `OPENAI_API_KEY` | Required if using OpenAI TTS | TTS access |
| `ELEVENLABS_API_KEY` | Required if using ElevenLabs | TTS access |

### 1.7 Storage

| Variable | Required | Purpose |
|----------|----------|---------|
| `STORAGE_PROVIDER` | Yes | `supabase`, `s3`, or compatible |
| `SUPABASE_STORAGE_BUCKET` | Required for Supabase storage | Voice files and artifacts |
| `STORAGE_BUCKET` | Required for S3-compatible storage | Voice files and artifacts |
| `AWS_ACCESS_KEY_ID` | Required for S3 | Storage access |
| `AWS_SECRET_ACCESS_KEY` | Required for S3 | Storage access |
| `AWS_REGION` | Required for S3 | Bucket region |
| `S3_ENDPOINT` | Optional | S3-compatible endpoint override |

### 1.8 Observability

| Variable | Required | Purpose |
|----------|----------|---------|
| `SENTRY_DSN` | Strongly recommended | Error monitoring |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Recommended | Traces/metrics |
| `LOG_LEVEL` | Yes | Example: `info` |

---

## 2. Mobile App Public Env Values

These values are safe to expose to the mobile client when prefixed for Expo public usage.

| Variable | Required | Purpose |
|----------|----------|---------|
| `EXPO_PUBLIC_API_URL` | Yes | Backend HTTP URL |
| `EXPO_PUBLIC_WS_URL` | Yes | Backend WebSocket URL |
| `EXPO_PUBLIC_APP_ENV` | Yes | App environment label |
| `EXPO_PUBLIC_SENTRY_DSN` | Optional | Client crash reporting |

---

## 3. Optional But Likely Needed Soon

| Variable | Required | Purpose |
|----------|----------|---------|
| `AUDIO_RETENTION_DAYS` | Optional | Voice artifact cleanup policy |
| `MAX_AUDIO_UPLOAD_MB` | Optional | Client upload cap |
| `DEFAULT_TIMEZONE` | Optional | Fallback scheduling timezone |
| `ALLOWED_ATTACHMENT_MIME_TYPES` | Optional | Upload validation |

---

## 4. Recommended First Config

If you want the fastest path to implementation, give me these values first:
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ENCRYPTION_KEY`
- `COMPOSIO_API_KEY`
- `COMPOSIO_WEBHOOK_SECRET`
- `COMPOSIO_GOOGLE_AUTH_CONFIG_ID`
- `COMPOSIO_MICROSOFT_AUTH_CONFIG_ID`
- `LLM_PROVIDER`
- `LLM_MODEL`
- one of `OPENAI_API_KEY` or `GOOGLE_API_KEY`
- `STT_PROVIDER`
- `STT_MODEL`
- one STT provider key
- `TTS_PROVIDER`
- `TTS_MODEL`
- `TTS_VOICE`
- one TTS provider key
- `EXPO_PUBLIC_API_URL`
- `EXPO_PUBLIC_WS_URL`

---

## 5. What You Can Send Me Next

The cleanest handoff format is:

```text
DATABASE_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
ENCRYPTION_KEY=
COMPOSIO_API_KEY=
COMPOSIO_WEBHOOK_SECRET=
COMPOSIO_GOOGLE_AUTH_CONFIG_ID=
COMPOSIO_MICROSOFT_AUTH_CONFIG_ID=
LLM_PROVIDER=
LLM_MODEL=
OPENAI_API_KEY=
GOOGLE_API_KEY=
STT_PROVIDER=
STT_MODEL=
GROQ_API_KEY=
DEEPGRAM_API_KEY=
TTS_PROVIDER=
TTS_MODEL=
TTS_VOICE=
ELEVENLABS_API_KEY=
EXPO_PUBLIC_API_URL=
EXPO_PUBLIC_WS_URL=
SENTRY_DSN=
```

You do not need to fill every provider-specific key. Only fill the ones for the providers we choose to use first.

### Current recommended provider set

For the current app setup, the recommended first stack is:
- `LLM_PROVIDER=google`
- `LLM_MODEL=gemini-2.5-flash`
- `STT_PROVIDER=groq`
- `STT_MODEL=whisper-large-v3-turbo`
- `TTS_PROVIDER=google`
- `TTS_MODEL=gemini-2.5-flash-preview-tts`
- `TTS_VOICE=Kore`

---

## 6. Which Env File To Use

For this repo:
- Backend reads, in order, `.env`, `apps/server/.env`, `.env.local`, and `apps/server/.env.local`
- Later files override earlier ones
- Mobile reads Expo public variables like `EXPO_PUBLIC_API_URL` from the Expo environment

Recommended setup:
- Put committed examples in `.env.example`
- Put your real secrets in `.env.local` at the repo root
- Use `apps/server/.env.local` only if you want backend-only overrides

If you want the simplest setup, use one root `.env.local` file for everything.
