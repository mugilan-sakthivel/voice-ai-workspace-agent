# Voice AI Workspace Agent

A cross-platform mobile app (iOS + Android) that acts as a **voice-activated AI agent** capable of executing any action in Google Workspace (and Microsoft 365) through natural language commands.

## Features

- **Push-to-Talk Voice Input** - Tap and hold to speak commands
- **AI-Powered Agent** - Uses DeepAgents (LangGraph) with Gemini for intelligent task execution
- **Google Workspace Integration** - Gmail, Calendar, Drive, Sheets, Docs via CLI
- **Voice Responses** - Natural text-to-speech responses using Gemini TTS
- **Claude-like UI** - Beautiful chat interface using assistant-ui
- **Conversation History** - Persistent threads with memory

## Tech Stack

### Mobile App
- React Native + Expo
- assistant-ui (LangGraph runtime)
- Zustand for state management

### Backend
- FastAPI (Python)
- DeepAgents / LangGraph
- Gemini 2.0 Flash (LLM)
- Groq Whisper (Speech-to-Text)
- Gemini TTS (Text-to-Speech)
- PostgreSQL + Redis

### Workspace Integration
- Google Workspace CLI (`gws`)
- Microsoft 365 CLI (`m365`) - Coming soon

## Architecture

See [docs/ARCHITECTURE-v2.md](docs/ARCHITECTURE-v2.md) for the complete system architecture.

## Quick Start

### Mobile App
```bash
npx assistant-ui@latest create -t langgraph my-voice-agent
cd my-voice-agent
npm install expo-av expo-secure-store expo-auth-session zustand
npx expo start
```

### Backend
```bash
pip install fastapi uvicorn langgraph langchain-google-genai groq psycopg2-binary redis cryptography
uvicorn app.main:app --reload
```

## Documentation

- [Architecture v2](docs/ARCHITECTURE-v2.md) - Complete system design
- [LLD](docs/LLD-Voice-AI-Agent.md) - Low-level design details
- [Critique](docs/LLD-CRITIQUE.md) - Design review and gaps

## References

- [DeepAgents](https://docs.langchain.com/oss/python/deepagents/overview)
- [Groq Whisper](https://console.groq.com/docs/speech-to-text)
- [Gemini TTS](https://ai.google.dev/gemini-api/docs/speech-generation)
- [Google Workspace CLI](https://github.com/googleworkspace/cli)
- [assistant-ui](https://www.assistant-ui.com/)
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview)

## License

MIT
