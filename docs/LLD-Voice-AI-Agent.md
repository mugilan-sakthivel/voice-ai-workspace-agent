# Low-Level Design: Voice AI Workspace Agent

## 1. Product Overview

### 1.1 Vision
A cross-platform mobile app (iOS + Android) that acts as a **voice-activated AI agent** capable of executing any action in Google Workspace and Microsoft 365 through natural language commands.

### 1.2 Core Features
- **Voice Activation**: Wake word detection ("Hey [AppName]") even when app is backgrounded
- **Voice Commands**: Natural language to workspace actions
- **Voice Response**: AI speaks back results/confirmations
- **Chat Interface**: Text-based interaction with conversation history
- **Workspace Integration**: Full control over Google & Microsoft productivity tools via CLI
- **AI Agent**: LangChain-powered agent with Gemini for intelligence

### 1.3 User Flow
```
User speaks "Hey Agent"
    → App wakes up & plays acknowledgment sound
    → User: "Schedule a meeting with John tomorrow at 3pm"
    → STT converts to text
    → AI Agent parses intent
    → Agent executes: gws calendar +insert ...
    → Agent speaks: "Done! Meeting scheduled with John for tomorrow 3pm"
```

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MOBILE APP (React Native + Expo)                  │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │  Wake Word      │  │  Voice I/O      │  │  Chat UI (assistant-ui)     │ │
│  │  Detection      │  │  Manager        │  │  - Thread view              │ │
│  │  (Background)   │  │                 │  │  - Message history          │ │
│  │                 │  │  - STT Stream   │  │  - Composer                 │ │
│  │  - Porcupine    │  │  - TTS Stream   │  │  - Attachments              │ │
│  │  - Vosk         │  │  - Audio Focus  │  │                             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
│           │                    │                         │                  │
│           └────────────────────┼─────────────────────────┘                  │
│                                ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      App State Management (Zustand)                   │  │
│  │  - Conversation State  - Auth State  - Settings  - CLI Results       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ WebSocket / REST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND SERVER                                  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    API Gateway (FastAPI / Node.js)                    │  │
│  │  - /api/v1/chat          - WebSocket for streaming                   │  │
│  │  - /api/v1/voice/stt     - /api/v1/auth/*                           │  │
│  │  - /api/v1/voice/tts     - /api/v1/conversations/*                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    AI AGENT CORE (LangChain + Gemini)                 │  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │  │
│  │  │   Intent    │  │    Task     │  │   Tool      │  │   Memory    │ │  │
│  │  │   Parser    │  │   Planner   │  │   Router    │  │   Manager   │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │  │
│  │         │                │                │                │        │  │
│  │         └────────────────┴────────────────┴────────────────┘        │  │
│  │                                   │                                  │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │                    TOOL EXECUTION ENGINE                      │   │  │
│  │  │                                                               │   │  │
│  │  │  ┌───────────────────┐       ┌───────────────────┐           │   │  │
│  │  │  │ Google Workspace  │       │  Microsoft 365    │           │   │  │
│  │  │  │ CLI Executor      │       │  CLI Executor     │           │   │  │
│  │  │  │                   │       │                   │           │   │  │
│  │  │  │ • gws drive       │       │ • m365 teams      │           │   │  │
│  │  │  │ • gws gmail       │       │ • m365 spo        │           │   │  │
│  │  │  │ • gws calendar    │       │ • m365 outlook    │           │   │  │
│  │  │  │ • gws sheets      │       │ • m365 onedrive   │           │   │  │
│  │  │  │ • gws docs        │       │ • m365 planner    │           │   │  │
│  │  │  │ • gws chat        │       │ • m365 todo       │           │   │  │
│  │  │  └───────────────────┘       └───────────────────┘           │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         VOICE PROCESSING                              │  │
│  │  ┌─────────────────────┐         ┌─────────────────────┐             │  │
│  │  │  Gemini STT         │         │  Gemini TTS         │             │  │
│  │  │  (Speech-to-Text)   │         │  (Text-to-Speech)   │             │  │
│  │  │  - Streaming        │         │  - 30 voices        │             │  │
│  │  │  - 77 languages     │         │  - Multi-speaker    │             │  │
│  │  └─────────────────────┘         └─────────────────────┘             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                      │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   PostgreSQL    │  │     Redis       │  │   Object Storage (S3)      │ │
│  │   - Users       │  │   - Sessions    │  │   - Voice recordings       │ │
│  │   - Convos      │  │   - Cache       │  │   - Attachments            │ │
│  │   - Messages    │  │   - Rate limits │  │   - Exports                │ │
│  │   - Auth tokens │  │                 │  │                             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Design

### 3.1 Mobile App Components

#### 3.1.1 Wake Word Detection Service

```typescript
// services/WakeWordService.ts

interface WakeWordConfig {
  keyword: string;           // "hey agent", "ok jarvis", etc.
  sensitivity: number;       // 0.0 - 1.0
  modelPath: string;         // Path to wake word model
}

interface WakeWordEvent {
  detected: boolean;
  confidence: number;
  timestamp: Date;
}

class WakeWordService {
  private porcupine: Porcupine | null = null;
  private isListening: boolean = false;
  private config: WakeWordConfig;

  // Initialize wake word detection
  async initialize(config: WakeWordConfig): Promise<void>;

  // Start listening in background
  async startListening(): Promise<void>;

  // Stop listening
  async stopListening(): Promise<void>;

  // Callback when wake word detected
  onWakeWordDetected(callback: (event: WakeWordEvent) => void): void;

  // Check if service is active
  isActive(): boolean;

  // Cleanup resources
  async destroy(): Promise<void>;
}
```

**Implementation Notes:**
- Use **Picovoice Porcupine** for wake word detection (works offline, low power)
- Runs as a foreground service on Android / background task on iOS
- Requires microphone permission with "always" access
- Battery optimization: Use voice activity detection (VAD) to reduce CPU

#### 3.1.2 Voice I/O Manager

```typescript
// services/VoiceIOManager.ts

interface VoiceIOConfig {
  sttEndpoint: string;
  ttsEndpoint: string;
  voiceName: string;        // Gemini voice: 'Kore', 'Puck', etc.
  language: string;         // 'en-US', 'es-ES', etc.
}

interface TranscriptionResult {
  text: string;
  confidence: number;
  isFinal: boolean;
  language: string;
}

interface SpeechSynthesisResult {
  audioData: ArrayBuffer;
  duration: number;
  format: 'wav' | 'mp3' | 'opus';
}

class VoiceIOManager {
  private audioRecorder: AudioRecorder;
  private audioPlayer: AudioPlayer;
  private wsConnection: WebSocket | null = null;
  private config: VoiceIOConfig;

  // Start recording and streaming to STT
  async startRecording(): Promise<void>;

  // Stop recording
  async stopRecording(): Promise<TranscriptionResult>;

  // Stream audio to STT (real-time transcription)
  async streamToSTT(audioChunk: ArrayBuffer): Promise<TranscriptionResult>;

  // Convert text to speech and play
  async speakText(text: string, options?: TTSOptions): Promise<void>;

  // Play acknowledgment sound
  async playAcknowledgmentSound(): Promise<void>;

  // Callbacks
  onTranscriptionUpdate(callback: (result: TranscriptionResult) => void): void;
  onSpeechStart(callback: () => void): void;
  onSpeechEnd(callback: () => void): void;

  // Audio focus management
  async requestAudioFocus(): Promise<boolean>;
  releaseAudioFocus(): void;
}
```

#### 3.1.3 Chat UI Components (assistant-ui - Claude-like Interface)

**Why assistant-ui?**
- Exact same sleek UI as Claude's chat interface
- React Native support for iOS & Android
- Built-in streaming, attachments, thread management
- Minimal bundle size, high performance

```typescript
// components/ChatInterface.tsx

import {
  AssistantRuntimeProvider,
  ThreadPrimitive,
  ComposerPrimitive,
  MessagePrimitive,
  AttachmentPrimitive,
  useLocalRuntime,
} from '@assistant-ui/react-native';

// ============================================
// THEME CONFIGURATION (Claude-like styling)
// ============================================

const theme = {
  colors: {
    // Light mode
    light: {
      background: '#FFFFFF',
      surface: '#F7F7F8',
      surfaceHover: '#EFEFEF',
      border: '#E5E5E6',
      textPrimary: '#1A1A1A',
      textSecondary: '#6B6B6B',
      textMuted: '#999999',
      accent: '#D97706',           // Orange accent (like Claude)
      accentHover: '#B45309',
      userBubble: '#F4F4F5',
      assistantBubble: 'transparent',
      success: '#10B981',
      error: '#EF4444',
      warning: '#F59E0B',
    },
    // Dark mode
    dark: {
      background: '#1A1A1A',
      surface: '#2D2D2D',
      surfaceHover: '#3D3D3D',
      border: '#404040',
      textPrimary: '#FFFFFF',
      textSecondary: '#A0A0A0',
      textMuted: '#666666',
      accent: '#F59E0B',
      accentHover: '#D97706',
      userBubble: '#2D2D2D',
      assistantBubble: 'transparent',
      success: '#34D399',
      error: '#F87171',
      warning: '#FBBF24',
    },
  },
  typography: {
    fontFamily: {
      sans: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
      mono: 'JetBrains Mono, Monaco, Consolas, monospace',
    },
    fontSize: {
      xs: 12,
      sm: 14,
      base: 16,
      lg: 18,
      xl: 20,
      '2xl': 24,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    '2xl': 32,
  },
  borderRadius: {
    sm: 6,
    md: 12,
    lg: 18,
    full: 9999,
  },
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px rgba(0, 0, 0, 0.07)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
  },
};

// ============================================
// MAIN CHAT SCREEN
// ============================================

const ChatScreen: React.FC = () => {
  const runtime = useLocalRuntime({
    // Connect to our backend
    endpoint: 'wss://api.voiceagent.app/ws/chat',
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <SafeAreaView style={styles.container}>
        {/* Header */}
        <Header />

        {/* Thread (Message List) */}
        <ThreadPrimitive.Root style={styles.thread}>
          <ThreadPrimitive.Viewport style={styles.viewport}>
            <ThreadPrimitive.Empty>
              <WelcomeScreen />
            </ThreadPrimitive.Empty>

            <ThreadPrimitive.Messages>
              {(message) => <MessageBubble message={message} />}
            </ThreadPrimitive.Messages>
          </ThreadPrimitive.Viewport>

          <ThreadPrimitive.ScrollToBottom style={styles.scrollToBottom}>
            <ChevronDownIcon />
          </ThreadPrimitive.ScrollToBottom>
        </ThreadPrimitive.Root>

        {/* Composer (Input Area) */}
        <ComposerBar />
      </SafeAreaView>
    </AssistantRuntimeProvider>
  );
};

// ============================================
// MESSAGE BUBBLE COMPONENT
// ============================================

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <MessagePrimitive.Root style={[
      styles.messageBubble,
      isUser ? styles.userBubble : styles.assistantBubble
    ]}>
      {/* Avatar */}
      {!isUser && (
        <View style={styles.avatar}>
          <AgentIcon />
        </View>
      )}

      <View style={styles.messageContent}>
        {/* Voice indicator if from voice input */}
        {message.voiceInput && (
          <View style={styles.voiceIndicator}>
            <MicIcon size={12} />
            <Text style={styles.voiceLabel}>Voice</Text>
          </View>
        )}

        {/* Message text */}
        <MessagePrimitive.Content>
          {(part) => {
            if (part.type === 'text') {
              return <Text style={styles.messageText}>{part.text}</Text>;
            }
            if (part.type === 'tool-call') {
              return <ToolCallCard toolCall={part} />;
            }
          }}
        </MessagePrimitive.Content>

        {/* Attachments */}
        <AttachmentPrimitive.Root>
          {(attachment) => <AttachmentPreview attachment={attachment} />}
        </AttachmentPrimitive.Root>

        {/* Timestamp */}
        <Text style={styles.timestamp}>
          {formatTime(message.createdAt)}
        </Text>
      </View>
    </MessagePrimitive.Root>
  );
};

// ============================================
// TOOL CALL DISPLAY (CLI Execution Results)
// ============================================

const ToolCallCard: React.FC<{ toolCall: ToolCall }> = ({ toolCall }) => {
  const getToolIcon = (tool: string) => {
    const icons: Record<string, JSX.Element> = {
      'google_calendar': <CalendarIcon />,
      'google_gmail': <MailIcon />,
      'google_drive': <FolderIcon />,
      'microsoft_teams': <TeamsIcon />,
      'microsoft_outlook': <MailIcon />,
      'microsoft_onedrive': <CloudIcon />,
    };
    return icons[tool] || <TerminalIcon />;
  };

  return (
    <View style={styles.toolCallCard}>
      <View style={styles.toolCallHeader}>
        {getToolIcon(toolCall.tool)}
        <Text style={styles.toolCallName}>
          {toolCall.tool}.{toolCall.action}
        </Text>
        {toolCall.success ? (
          <CheckCircleIcon color={theme.colors.light.success} />
        ) : (
          <XCircleIcon color={theme.colors.light.error} />
        )}
      </View>

      {toolCall.result && (
        <View style={styles.toolCallResult}>
          <Text style={styles.toolCallResultText}>
            {typeof toolCall.result === 'string'
              ? toolCall.result
              : JSON.stringify(toolCall.result, null, 2)}
          </Text>
        </View>
      )}
    </View>
  );
};

// ============================================
// COMPOSER BAR (Input + Voice Button)
// ============================================

const ComposerBar: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const { startRecording, stopRecording } = useVoice();

  const handleVoicePress = async () => {
    if (isRecording) {
      const transcription = await stopRecording();
      // Transcription is automatically sent
      setIsRecording(false);
    } else {
      await startRecording();
      setIsRecording(true);
    }
  };

  return (
    <View style={styles.composerContainer}>
      <ComposerPrimitive.Root style={styles.composer}>
        {/* Attachment button */}
        <ComposerPrimitive.AddAttachment style={styles.attachButton}>
          <PaperclipIcon />
        </ComposerPrimitive.AddAttachment>

        {/* Text input */}
        <ComposerPrimitive.Input
          style={styles.composerInput}
          placeholder="Message Voice Agent..."
          placeholderTextColor={theme.colors.light.textMuted}
        />

        {/* Voice button */}
        <TouchableOpacity
          style={[
            styles.voiceButton,
            isRecording && styles.voiceButtonRecording
          ]}
          onPress={handleVoicePress}
        >
          {isRecording ? (
            <View style={styles.recordingIndicator}>
              <Animated.View style={styles.recordingPulse} />
              <StopIcon color="#FFFFFF" />
            </View>
          ) : (
            <MicIcon color={theme.colors.light.accent} />
          )}
        </TouchableOpacity>

        {/* Send button */}
        <ComposerPrimitive.Send style={styles.sendButton}>
          <SendIcon />
        </ComposerPrimitive.Send>
      </ComposerPrimitive.Root>
    </View>
  );
};

// ============================================
// VOICE RECORDING OVERLAY
// ============================================

const VoiceRecordingOverlay: React.FC<{
  isVisible: boolean;
  transcription: string;
  onCancel: () => void;
}> = ({ isVisible, transcription, onCancel }) => {
  if (!isVisible) return null;

  return (
    <Modal transparent animationType="fade">
      <View style={styles.voiceOverlay}>
        <View style={styles.voiceOverlayContent}>
          {/* Animated waveform */}
          <AudioWaveform />

          {/* Live transcription */}
          <Text style={styles.liveTranscription}>
            {transcription || 'Listening...'}
          </Text>

          {/* Cancel button */}
          <TouchableOpacity onPress={onCancel} style={styles.cancelButton}>
            <Text style={styles.cancelText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

// ============================================
// WELCOME SCREEN (Empty State)
// ============================================

const WelcomeScreen: React.FC = () => (
  <View style={styles.welcomeContainer}>
    <AgentLogo size={64} />
    <Text style={styles.welcomeTitle}>Voice Agent</Text>
    <Text style={styles.welcomeSubtitle}>
      Your AI assistant for Google & Microsoft workspace
    </Text>

    <View style={styles.suggestionChips}>
      <SuggestionChip text="What's on my calendar today?" />
      <SuggestionChip text="Show unread emails" />
      <SuggestionChip text="Create a new document" />
      <SuggestionChip text="Schedule a meeting" />
    </View>
  </View>
);

// ============================================
// STYLES (Claude-like)
// ============================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.light.background,
  },
  thread: {
    flex: 1,
  },
  viewport: {
    flex: 1,
    paddingHorizontal: theme.spacing.lg,
  },
  messageBubble: {
    flexDirection: 'row',
    marginVertical: theme.spacing.sm,
    maxWidth: '85%',
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: theme.colors.light.userBubble,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.md,
  },
  assistantBubble: {
    alignSelf: 'flex-start',
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.light.accent,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: theme.spacing.sm,
  },
  messageContent: {
    flex: 1,
  },
  messageText: {
    fontSize: theme.typography.fontSize.base,
    lineHeight: theme.typography.fontSize.base * theme.typography.lineHeight.relaxed,
    color: theme.colors.light.textPrimary,
  },
  toolCallCard: {
    backgroundColor: theme.colors.light.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginTop: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.light.border,
  },
  toolCallHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.sm,
  },
  toolCallName: {
    flex: 1,
    fontSize: theme.typography.fontSize.sm,
    fontFamily: theme.typography.fontFamily.mono,
    color: theme.colors.light.textSecondary,
  },
  composerContainer: {
    borderTopWidth: 1,
    borderTopColor: theme.colors.light.border,
    padding: theme.spacing.md,
  },
  composer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.light.surface,
    borderRadius: theme.borderRadius.lg,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
  },
  composerInput: {
    flex: 1,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.light.textPrimary,
    paddingVertical: theme.spacing.sm,
  },
  voiceButton: {
    width: 40,
    height: 40,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.light.surface,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: theme.spacing.xs,
  },
  voiceButtonRecording: {
    backgroundColor: theme.colors.light.error,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: theme.borderRadius.full,
    backgroundColor: theme.colors.light.accent,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

// ============================================
// DATA TYPES
// ============================================

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: Date;
  voiceInput?: boolean;      // Was this from voice?
  attachments?: Attachment[];
  toolCalls?: ToolCall[];    // CLI commands executed
}

interface ToolCall {
  id: string;
  tool: string;              // 'google_calendar', 'microsoft_teams', etc.
  action: string;            // 'create', 'list', 'send', etc.
  input: Record<string, any>;
  result?: any;
  success: boolean;
  error?: string;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
  workspace: 'google' | 'microsoft' | 'both';
}
```

**Component Hierarchy:**
```
App
├── AssistantRuntimeProvider          ← assistant-ui context
├── NavigationContainer
│   ├── DrawerNavigator
│   │   ├── ConversationListScreen    ← Thread history (drawer)
│   │   ├── ChatScreen
│   │   │   ├── Header
│   │   │   ├── ThreadPrimitive.Root
│   │   │   │   ├── ThreadPrimitive.Empty → WelcomeScreen
│   │   │   │   ├── ThreadPrimitive.Messages
│   │   │   │   │   ├── MessageBubble
│   │   │   │   │   │   ├── Avatar
│   │   │   │   │   │   ├── MessagePrimitive.Content
│   │   │   │   │   │   ├── ToolCallCard
│   │   │   │   │   │   └── AttachmentPreview
│   │   │   │   │   └── ...
│   │   │   │   └── ThreadPrimitive.ScrollToBottom
│   │   │   ├── ComposerBar
│   │   │   │   ├── ComposerPrimitive.AddAttachment
│   │   │   │   ├── ComposerPrimitive.Input
│   │   │   │   ├── VoiceButton (custom)
│   │   │   │   └── ComposerPrimitive.Send
│   │   │   └── VoiceRecordingOverlay
│   │   ├── SettingsScreen
│   │   └── AccountsScreen            ← Connect Google/Microsoft
│   └── AuthStack
│       ├── OnboardingScreen
│       ├── GoogleAuthScreen
│       └── MicrosoftAuthScreen
```

#### 3.1.4 App State Management

```typescript
// store/appStore.ts (Zustand)

interface AppState {
  // Auth State
  user: User | null;
  googleAuth: OAuthTokens | null;
  microsoftAuth: OAuthTokens | null;

  // Conversation State
  conversations: Conversation[];
  activeConversationId: string | null;

  // Voice State
  isListening: boolean;
  isRecording: boolean;
  isSpeaking: boolean;
  wakeWordEnabled: boolean;

  // Settings
  settings: AppSettings;

  // Actions
  setUser: (user: User) => void;
  addMessage: (conversationId: string, message: Message) => void;
  createConversation: () => Conversation;
  setVoiceState: (state: Partial<VoiceState>) => void;
  updateSettings: (settings: Partial<AppSettings>) => void;
}

interface AppSettings {
  voiceName: string;           // TTS voice
  wakeWord: string;            // Custom wake word
  autoSpeak: boolean;          // Auto-speak responses
  language: string;
  defaultWorkspace: 'google' | 'microsoft' | 'ask';
}
```

---

### 3.2 Backend Components

#### 3.2.1 API Gateway

```python
# api/main.py (FastAPI)

from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Voice AI Agent API", version="1.0.0")

# REST Endpoints
@app.post("/api/v1/chat")
async def chat(request: ChatRequest, user: User = Depends(get_current_user)):
    """Process a chat message and return AI response with tool executions"""
    pass

@app.post("/api/v1/voice/stt")
async def speech_to_text(audio: UploadFile, user: User = Depends(get_current_user)):
    """Convert audio to text using Gemini STT"""
    pass

@app.post("/api/v1/voice/tts")
async def text_to_speech(request: TTSRequest, user: User = Depends(get_current_user)):
    """Convert text to speech using Gemini TTS"""
    pass

@app.get("/api/v1/conversations")
async def list_conversations(user: User = Depends(get_current_user)):
    """Get user's conversation history"""
    pass

@app.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, user: User = Depends(get_current_user)):
    """Get a specific conversation with all messages"""
    pass

# WebSocket for streaming
@app.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """Real-time streaming chat with voice support"""
    pass

# OAuth endpoints
@app.get("/api/v1/auth/google/authorize")
async def google_auth_url():
    """Get Google OAuth authorization URL"""
    pass

@app.post("/api/v1/auth/google/callback")
async def google_auth_callback(code: str):
    """Handle Google OAuth callback"""
    pass

@app.get("/api/v1/auth/microsoft/authorize")
async def microsoft_auth_url():
    """Get Microsoft OAuth authorization URL"""
    pass

@app.post("/api/v1/auth/microsoft/callback")
async def microsoft_auth_callback(code: str):
    """Handle Microsoft OAuth callback"""
    pass
```

#### 3.2.2 AI Agent Core (LangChain + Gemini)

```python
# agent/core.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class VoiceAIAgent:
    """
    Main AI Agent that processes user commands and executes workspace actions.
    """

    def __init__(
        self,
        google_credentials: dict | None = None,
        microsoft_credentials: dict | None = None,
        user_id: str = None
    ):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            convert_system_message_to_human=True
        )

        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=20  # Keep last 20 messages
        )

        self.tools = self._initialize_tools(google_credentials, microsoft_credentials)
        self.agent = self._create_agent()
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )

    def _initialize_tools(self, google_creds, microsoft_creds) -> list:
        """Initialize all available tools based on user's connected accounts"""
        tools = []

        if google_creds:
            tools.extend([
                GoogleDriveTool(google_creds),
                GoogleGmailTool(google_creds),
                GoogleCalendarTool(google_creds),
                GoogleSheetsTool(google_creds),
                GoogleDocsTool(google_creds),
                GoogleChatTool(google_creds),
            ])

        if microsoft_creds:
            tools.extend([
                MicrosoftTeamsTool(microsoft_creds),
                MicrosoftOutlookTool(microsoft_creds),
                MicrosoftOneDriveTool(microsoft_creds),
                MicrosoftSharePointTool(microsoft_creds),
                MicrosoftPlannerTool(microsoft_creds),
                MicrosoftToDoTool(microsoft_creds),
            ])

        return tools

    def _create_agent(self):
        """Create the LangChain agent with system prompt"""

        system_prompt = """You are a helpful voice-activated AI assistant that helps users manage their workspace productivity tools.

You have access to both Google Workspace (Drive, Gmail, Calendar, Sheets, Docs, Chat) and Microsoft 365 (Teams, Outlook, OneDrive, SharePoint, Planner, ToDo).

Guidelines:
1. Always confirm what action you're about to take before executing
2. For ambiguous requests, ask clarifying questions
3. After executing an action, summarize what you did
4. If an action fails, explain why and suggest alternatives
5. Be concise in responses since many will be spoken aloud
6. When handling sensitive data (emails, files), be cautious and ask for confirmation

Current user's connected services: {connected_services}
Current date/time: {current_datetime}
User's timezone: {user_timezone}

Remember: Your responses will often be converted to speech, so keep them clear and concise."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        return create_tool_calling_agent(self.llm, self.tools, prompt)

    async def process_command(self, user_input: str, context: dict = None) -> AgentResponse:
        """
        Process a user command and return the response with any tool executions.
        """
        try:
            result = await self.executor.ainvoke({
                "input": user_input,
                "connected_services": context.get("connected_services", ""),
                "current_datetime": context.get("current_datetime", ""),
                "user_timezone": context.get("user_timezone", "UTC"),
            })

            return AgentResponse(
                success=True,
                response=result["output"],
                tool_calls=self._extract_tool_calls(result),
                memory_updated=True
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"I encountered an error: {str(e)}",
                error=str(e)
            )

    async def stream_response(self, user_input: str, context: dict = None):
        """Stream the response for real-time display"""
        async for chunk in self.executor.astream({
            "input": user_input,
            **context
        }):
            yield chunk
```

#### 3.2.3 CLI Tool Wrappers

```python
# agent/tools/google_workspace.py

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import subprocess
import json

class GoogleDriveTool(BaseTool):
    """Tool for interacting with Google Drive via gws CLI"""

    name = "google_drive"
    description = """
    Manage files and folders in Google Drive.

    Capabilities:
    - List files: list files in Drive or a specific folder
    - Search files: search for files by name or content
    - Upload files: upload a file to Drive
    - Download files: download a file from Drive
    - Create folders: create new folders
    - Share files: share files with specific users
    - Move files: move files between folders
    - Delete files: move files to trash

    Examples:
    - "List my recent files" -> action: list, params: {orderBy: "modifiedTime desc", pageSize: 10}
    - "Search for budget spreadsheet" -> action: search, params: {q: "name contains 'budget'"}
    - "Share report.pdf with john@company.com" -> action: share, params: {fileId: "...", email: "john@company.com"}
    """

    credentials: dict = None

    class InputSchema(BaseModel):
        action: str = Field(description="The action to perform: list, search, upload, download, create_folder, share, move, delete")
        params: dict = Field(description="Parameters for the action as a JSON object")

    def _run(self, action: str, params: dict) -> str:
        """Execute Google Drive command via gws CLI"""

        command_map = {
            "list": self._list_files,
            "search": self._search_files,
            "upload": self._upload_file,
            "download": self._download_file,
            "create_folder": self._create_folder,
            "share": self._share_file,
            "move": self._move_file,
            "delete": self._delete_file,
        }

        if action not in command_map:
            return f"Unknown action: {action}. Available actions: {list(command_map.keys())}"

        return command_map[action](params)

    def _execute_gws(self, command: str) -> dict:
        """Execute gws CLI command and return JSON result"""
        try:
            result = subprocess.run(
                f"gws {command}",
                shell=True,
                capture_output=True,
                text=True,
                env={**os.environ, "GOOGLE_WORKSPACE_CLI_TOKEN": self.credentials["access_token"]}
            )

            if result.returncode != 0:
                return {"error": result.stderr}

            return json.loads(result.stdout)
        except Exception as e:
            return {"error": str(e)}

    def _list_files(self, params: dict) -> str:
        """List files in Drive"""
        page_size = params.get("pageSize", 10)
        order_by = params.get("orderBy", "modifiedTime desc")
        folder_id = params.get("folderId", "root")

        query = f"'{folder_id}' in parents and trashed = false"

        result = self._execute_gws(
            f"drive files list --params '{{\"q\": \"{query}\", \"pageSize\": {page_size}, \"orderBy\": \"{order_by}\", \"fields\": \"files(id,name,mimeType,modifiedTime,size)\"}}'"
        )

        if "error" in result:
            return f"Error listing files: {result['error']}"

        files = result.get("files", [])
        if not files:
            return "No files found."

        response = "Found files:\n"
        for f in files:
            response += f"- {f['name']} ({f['mimeType']}) - Modified: {f['modifiedTime']}\n"

        return response

    def _search_files(self, params: dict) -> str:
        """Search for files"""
        query = params.get("q", "")
        result = self._execute_gws(
            f"drive files list --params '{{\"q\": \"{query}\", \"pageSize\": 20, \"fields\": \"files(id,name,mimeType,webViewLink)\"}}'"
        )

        if "error" in result:
            return f"Error searching: {result['error']}"

        files = result.get("files", [])
        if not files:
            return f"No files found matching: {query}"

        response = f"Found {len(files)} files:\n"
        for f in files:
            response += f"- {f['name']}: {f.get('webViewLink', 'No link')}\n"

        return response

    # ... more methods for upload, download, share, etc.


class GoogleGmailTool(BaseTool):
    """Tool for interacting with Gmail via gws CLI"""

    name = "google_gmail"
    description = """
    Manage emails in Gmail.

    Capabilities:
    - List emails: get recent emails or search
    - Read email: get full content of an email
    - Send email: compose and send new emails
    - Reply to email: reply to existing threads
    - Forward email: forward emails to others
    - Search emails: search by sender, subject, date, etc.
    - Label emails: add/remove labels
    - Archive/Delete: manage email organization

    Examples:
    - "Show my unread emails" -> action: list, params: {q: "is:unread", maxResults: 10}
    - "Send email to boss about project update" -> action: send, params: {to: "boss@company.com", subject: "Project Update", body: "..."}
    - "Search emails from John last week" -> action: search, params: {q: "from:john after:2024/01/01"}
    """

    credentials: dict = None

    def _run(self, action: str, params: dict) -> str:
        """Execute Gmail command via gws CLI"""

        if action == "list":
            return self._list_emails(params)
        elif action == "read":
            return self._read_email(params)
        elif action == "send":
            return self._send_email(params)
        elif action == "reply":
            return self._reply_email(params)
        elif action == "search":
            return self._search_emails(params)
        else:
            return f"Unknown action: {action}"

    def _send_email(self, params: dict) -> str:
        """Send an email using gws +send helper"""
        to = params.get("to")
        subject = params.get("subject")
        body = params.get("body")
        cc = params.get("cc", "")

        # Use gws helper command
        cmd = f'+send --to "{to}" --subject "{subject}" --body "{body}"'
        if cc:
            cmd += f' --cc "{cc}"'

        result = self._execute_gws(cmd)

        if "error" in result:
            return f"Failed to send email: {result['error']}"

        return f"Email sent successfully to {to}"


class GoogleCalendarTool(BaseTool):
    """Tool for interacting with Google Calendar via gws CLI"""

    name = "google_calendar"
    description = """
    Manage Google Calendar events.

    Capabilities:
    - List events: get upcoming events or events on specific dates
    - Create event: schedule new meetings/events
    - Update event: modify existing events
    - Delete event: cancel events
    - Check availability: find free time slots
    - Invite attendees: add people to events

    Examples:
    - "What's on my calendar today" -> action: agenda, params: {timeMin: "today", timeMax: "tomorrow"}
    - "Schedule meeting with John tomorrow at 3pm" -> action: create, params: {summary: "Meeting with John", start: "tomorrow 3pm", attendees: ["john@company.com"]}
    - "Cancel my 4pm meeting" -> action: delete, params: {eventId: "..."}
    """

    credentials: dict = None

    def _run(self, action: str, params: dict) -> str:
        if action == "agenda":
            return self._get_agenda(params)
        elif action == "create":
            return self._create_event(params)
        elif action == "update":
            return self._update_event(params)
        elif action == "delete":
            return self._delete_event(params)
        elif action == "availability":
            return self._check_availability(params)
        else:
            return f"Unknown action: {action}"

    def _create_event(self, params: dict) -> str:
        """Create calendar event using gws +insert helper"""
        summary = params.get("summary")
        start = params.get("start")
        end = params.get("end", "")
        attendees = params.get("attendees", [])
        description = params.get("description", "")

        # Use natural language time parsing
        cmd = f'+insert --summary "{summary}" --start "{start}"'
        if end:
            cmd += f' --end "{end}"'
        if attendees:
            cmd += f' --attendees "{",".join(attendees)}"'
        if description:
            cmd += f' --description "{description}"'

        result = self._execute_gws(cmd)

        if "error" in result:
            return f"Failed to create event: {result['error']}"

        return f"Event '{summary}' created successfully"

    def _get_agenda(self, params: dict) -> str:
        """Get calendar agenda using gws +agenda helper"""
        result = self._execute_gws("+agenda")

        if "error" in result:
            return f"Failed to get agenda: {result['error']}"

        return result.get("formatted", "No events found")


# Similar implementations for:
# - GoogleSheetsTool (list, read, append, update cells)
# - GoogleDocsTool (create, read, update documents)
# - GoogleChatTool (send messages to spaces)
```

```python
# agent/tools/microsoft365.py

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import subprocess
import json

class MicrosoftTeamsTool(BaseTool):
    """Tool for interacting with Microsoft Teams via m365 CLI"""

    name = "microsoft_teams"
    description = """
    Manage Microsoft Teams.

    Capabilities:
    - List teams: get user's teams
    - List channels: get channels in a team
    - Send message: post to a channel
    - Create meeting: schedule Teams meeting
    - List chats: get recent chats
    - Send chat: send direct message

    Examples:
    - "Post 'Hello team' to general channel" -> action: post, params: {teamName: "...", channelName: "General", message: "Hello team"}
    - "Schedule a Teams meeting tomorrow" -> action: meeting, params: {subject: "...", start: "tomorrow 2pm"}
    """

    credentials: dict = None

    def _execute_m365(self, command: str) -> dict:
        """Execute m365 CLI command"""
        try:
            # Set auth token via environment
            env = {
                **os.environ,
                "CLIMICROSOFT365_ACCESSTOKEN": self.credentials["access_token"]
            }

            result = subprocess.run(
                f"m365 {command} --output json",
                shell=True,
                capture_output=True,
                text=True,
                env=env
            )

            if result.returncode != 0:
                return {"error": result.stderr}

            return json.loads(result.stdout) if result.stdout else {}
        except Exception as e:
            return {"error": str(e)}

    def _run(self, action: str, params: dict) -> str:
        if action == "list_teams":
            return self._list_teams()
        elif action == "list_channels":
            return self._list_channels(params)
        elif action == "post":
            return self._post_message(params)
        elif action == "meeting":
            return self._create_meeting(params)
        elif action == "list_chats":
            return self._list_chats()
        elif action == "send_chat":
            return self._send_chat(params)
        else:
            return f"Unknown action: {action}"

    def _list_teams(self) -> str:
        result = self._execute_m365("teams team list")

        if "error" in result:
            return f"Error listing teams: {result['error']}"

        teams = result if isinstance(result, list) else []
        if not teams:
            return "No teams found"

        response = "Your teams:\n"
        for team in teams:
            response += f"- {team.get('displayName')}\n"

        return response

    def _post_message(self, params: dict) -> str:
        team_name = params.get("teamName")
        channel_name = params.get("channelName", "General")
        message = params.get("message")

        # First get team ID
        teams = self._execute_m365(f'teams team list --query "[?displayName==\'{team_name}\']"')
        if not teams or "error" in teams:
            return f"Team '{team_name}' not found"

        team_id = teams[0]["id"]

        # Get channel ID
        channels = self._execute_m365(f'teams channel list --teamId {team_id} --query "[?displayName==\'{channel_name}\']"')
        if not channels or "error" in channels:
            return f"Channel '{channel_name}' not found"

        channel_id = channels[0]["id"]

        # Post message
        result = self._execute_m365(
            f'teams message send --teamId {team_id} --channelId {channel_id} --message "{message}"'
        )

        if "error" in result:
            return f"Failed to post message: {result['error']}"

        return f"Message posted to {team_name}/{channel_name}"


class MicrosoftOutlookTool(BaseTool):
    """Tool for interacting with Outlook via m365 CLI"""

    name = "microsoft_outlook"
    description = """
    Manage Outlook emails and calendar.

    Capabilities:
    - List emails: get recent or unread emails
    - Send email: compose and send emails
    - Reply/Forward: respond to emails
    - Calendar: list and create events
    - Search: find emails by criteria

    Examples:
    - "Show unread Outlook emails" -> action: list, params: {filter: "isRead eq false"}
    - "Send email via Outlook to..." -> action: send, params: {to: "...", subject: "...", body: "..."}
    """

    credentials: dict = None

    def _run(self, action: str, params: dict) -> str:
        if action == "list":
            return self._list_emails(params)
        elif action == "send":
            return self._send_email(params)
        elif action == "calendar":
            return self._list_calendar(params)
        elif action == "create_event":
            return self._create_event(params)
        else:
            return f"Unknown action: {action}"

    def _send_email(self, params: dict) -> str:
        to = params.get("to")
        subject = params.get("subject")
        body = params.get("body")

        result = self._execute_m365(
            f'outlook mail send --to "{to}" --subject "{subject}" --bodyContents "{body}"'
        )

        if "error" in result:
            return f"Failed to send email: {result['error']}"

        return f"Email sent to {to}"


class MicrosoftOneDriveTool(BaseTool):
    """Tool for OneDrive file operations"""
    name = "microsoft_onedrive"
    description = """Manage files in OneDrive: list, upload, download, share, search files."""
    # Implementation similar to Google Drive


class MicrosoftPlannerTool(BaseTool):
    """Tool for Microsoft Planner task management"""
    name = "microsoft_planner"
    description = """Manage Planner tasks: list plans, create tasks, update status, assign tasks."""
    # Implementation for Planner


class MicrosoftToDoTool(BaseTool):
    """Tool for Microsoft To Do"""
    name = "microsoft_todo"
    description = """Manage To Do tasks: list tasks, create tasks, complete tasks, set due dates."""
    # Implementation for To Do
```

#### 3.2.4 Voice Processing Service

```python
# services/voice_service.py

import google.generativeai as genai
from google.generativeai import types
import io
import wave

class GeminiVoiceService:
    """
    Voice processing using Google Gemini API.
    Handles both STT (Speech-to-Text) and TTS (Text-to-Speech).
    """

    AVAILABLE_VOICES = [
        "Aoede", "Charon", "Fenrir", "Kore", "Puck", "Zephyr",
        "Leda", "Orus", "Perseus", "Vesta", "Calliope", "Autonoe",
        # ... 30 total voices
    ]

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.tts_model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")
        self.stt_model = genai.GenerativeModel("gemini-2.0-flash")  # For multimodal audio input

    async def speech_to_text(self, audio_data: bytes, language: str = "en-US") -> TranscriptionResult:
        """
        Convert speech audio to text using Gemini's multimodal capabilities.
        """
        try:
            # Upload audio as inline data
            response = await self.stt_model.generate_content_async([
                "Transcribe this audio accurately. Return only the transcription, nothing else.",
                {
                    "mime_type": "audio/wav",
                    "data": audio_data
                }
            ])

            return TranscriptionResult(
                text=response.text.strip(),
                confidence=0.95,  # Gemini doesn't provide confidence scores
                language=language,
                is_final=True
            )
        except Exception as e:
            raise VoiceProcessingError(f"STT failed: {str(e)}")

    async def text_to_speech(
        self,
        text: str,
        voice_name: str = "Kore",
        style_prompt: str = None
    ) -> bytes:
        """
        Convert text to speech using Gemini TTS.

        Args:
            text: The text to speak
            voice_name: One of the 30 available voices
            style_prompt: Optional style direction (e.g., "cheerfully", "professionally")
        """
        try:
            # Construct the prompt with style if provided
            if style_prompt:
                content = f"Say {style_prompt}: {text}"
            else:
                content = text

            response = await self.tts_model.generate_content_async(
                content,
                generation_config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    )
                )
            )

            # Extract audio data from response
            audio_data = response.candidates[0].content.parts[0].inline_data.data

            return audio_data

        except Exception as e:
            raise VoiceProcessingError(f"TTS failed: {str(e)}")

    async def generate_acknowledgment_sound(self) -> bytes:
        """Generate a short acknowledgment sound when wake word is detected"""
        return await self.text_to_speech(
            "Hmm?",
            voice_name="Kore",
            style_prompt="as a brief, friendly acknowledgment"
        )


class TranscriptionResult:
    def __init__(self, text: str, confidence: float, language: str, is_final: bool):
        self.text = text
        self.confidence = confidence
        self.language = language
        self.is_final = is_final


class VoiceProcessingError(Exception):
    pass
```

---

## 4. Database Schema

### 4.1 PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb
);

-- OAuth credentials (encrypted)
CREATE TABLE oauth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google' or 'microsoft'
    access_token_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT NOT NULL,
    token_expiry TIMESTAMP WITH TIME ZONE,
    scopes TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, provider)
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    workspace_context VARCHAR(50) DEFAULT 'both', -- 'google', 'microsoft', 'both'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    archived_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    voice_input BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb -- voice duration, confidence, etc.
);

-- Tool calls (CLI executions)
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL, -- 'google_calendar', 'microsoft_teams', etc.
    action VARCHAR(100) NOT NULL, -- 'create', 'list', 'send', etc.
    input_params JSONB NOT NULL,
    output_result JSONB,
    success BOOLEAN,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_tool_calls_message_id ON tool_calls(message_id);
CREATE INDEX idx_tool_calls_tool_name ON tool_calls(tool_name);

-- Full-text search on messages
CREATE INDEX idx_messages_content_search ON messages USING gin(to_tsvector('english', content));
```

### 4.2 Redis Schema

```
# Session management
session:{user_id} -> {
    "active_conversation_id": "uuid",
    "connected_services": ["google", "microsoft"],
    "last_activity": "timestamp"
}
TTL: 24 hours

# Rate limiting
ratelimit:chat:{user_id} -> count
TTL: 1 minute (reset)

ratelimit:voice:{user_id} -> count
TTL: 1 minute

# Conversation context cache
context:{conversation_id} -> {
    "recent_messages": [...],
    "active_tools": [...],
    "user_timezone": "America/New_York"
}
TTL: 1 hour

# OAuth token cache (avoid DB lookups)
oauth:{user_id}:{provider} -> {
    "access_token": "encrypted",
    "expires_at": "timestamp"
}
TTL: Until token expiry
```

---

## 5. API Contracts

### 5.1 REST API Endpoints

#### Chat Endpoint

```yaml
POST /api/v1/chat
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request:
{
  "conversation_id": "uuid",  # Optional, creates new if omitted
  "message": "Schedule a meeting with John tomorrow at 3pm",
  "voice_input": false,
  "context": {
    "preferred_workspace": "google"  # Optional hint
  }
}

Response:
{
  "conversation_id": "uuid",
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "I've scheduled a meeting with John tomorrow at 3:00 PM. I've sent an invite to john@company.com. Is there anything else you'd like me to add to the meeting?",
    "created_at": "2024-01-15T10:30:00Z",
    "tool_calls": [
      {
        "id": "uuid",
        "tool": "google_calendar",
        "action": "create",
        "input": {
          "summary": "Meeting with John",
          "start": "2024-01-16T15:00:00",
          "attendees": ["john@company.com"]
        },
        "output": {
          "event_id": "abc123",
          "html_link": "https://calendar.google.com/event?eid=abc123"
        },
        "success": true
      }
    ]
  }
}
```

#### Voice STT Endpoint

```yaml
POST /api/v1/voice/stt
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

Request:
- audio: <binary audio file> (WAV, MP3, or WebM)
- language: "en-US" (optional)

Response:
{
  "transcription": {
    "text": "Schedule a meeting with John tomorrow at 3pm",
    "confidence": 0.95,
    "language": "en-US",
    "duration_ms": 3500
  }
}
```

#### Voice TTS Endpoint

```yaml
POST /api/v1/voice/tts
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request:
{
  "text": "I've scheduled the meeting for you.",
  "voice": "Kore",
  "style": "professional",  # Optional
  "format": "mp3"  # wav, mp3, opus
}

Response:
Content-Type: audio/mp3
<binary audio data>
```

#### Conversations List

```yaml
GET /api/v1/conversations
Authorization: Bearer {jwt_token}

Query Parameters:
- limit: 20 (default)
- offset: 0
- archived: false

Response:
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Meeting scheduling",
      "preview": "Schedule a meeting with John...",
      "message_count": 5,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "workspace": "google"
    }
  ],
  "total": 45,
  "has_more": true
}
```

### 5.2 WebSocket Protocol

```yaml
# Connect
ws://api.voiceagent.com/ws/chat/{conversation_id}
Headers:
  Authorization: Bearer {jwt_token}

# Client -> Server Messages

## Send chat message
{
  "type": "chat",
  "message": "What's on my calendar today?",
  "voice_input": false
}

## Send audio chunk (streaming STT)
{
  "type": "audio_chunk",
  "data": "<base64 encoded audio>",
  "sequence": 1,
  "is_final": false
}

## End audio stream
{
  "type": "audio_end"
}

# Server -> Client Messages

## Transcription update (real-time)
{
  "type": "transcription",
  "text": "What's on my calendar",
  "is_final": false
}

## Agent thinking
{
  "type": "thinking",
  "status": "Processing your request..."
}

## Tool execution start
{
  "type": "tool_start",
  "tool": "google_calendar",
  "action": "agenda"
}

## Tool execution complete
{
  "type": "tool_complete",
  "tool": "google_calendar",
  "action": "agenda",
  "success": true,
  "result_preview": "Found 3 events"
}

## Response streaming
{
  "type": "response_chunk",
  "content": "You have ",
  "is_final": false
}

## Response complete
{
  "type": "response_complete",
  "message": {
    "id": "uuid",
    "content": "You have 3 events today...",
    "tool_calls": [...]
  }
}

## Audio response (TTS)
{
  "type": "audio_response",
  "data": "<base64 encoded audio>",
  "duration_ms": 5000
}

## Error
{
  "type": "error",
  "code": "tool_execution_failed",
  "message": "Failed to access calendar"
}
```

---

## 6. Sequence Diagrams

### 6.1 Voice Command Flow

```
┌──────┐          ┌──────────┐       ┌─────────┐       ┌─────────┐      ┌──────────┐
│ User │          │Mobile App│       │ Backend │       │AI Agent │      │   CLI    │
└──┬───┘          └────┬─────┘       └────┬────┘       └────┬────┘      └────┬─────┘
   │                   │                  │                 │                │
   │ "Hey Agent"       │                  │                 │                │
   │──────────────────>│                  │                 │                │
   │                   │                  │                 │                │
   │                   │ Wake word detected                 │                │
   │                   │ Play ack sound   │                 │                │
   │   *ding*          │                  │                 │                │
   │<──────────────────│                  │                 │                │
   │                   │                  │                 │                │
   │ "Schedule meeting │                  │                 │                │
   │  with John at 3pm"│                  │                 │                │
   │──────────────────>│                  │                 │                │
   │                   │                  │                 │                │
   │                   │ Stream audio     │                 │                │
   │                   │─────────────────>│                 │                │
   │                   │                  │                 │                │
   │                   │                  │ STT Processing  │                │
   │                   │                  │────────────────>│                │
   │                   │                  │                 │                │
   │                   │ Transcription    │                 │                │
   │                   │<─────────────────│                 │                │
   │                   │                  │                 │                │
   │ Show transcription│                  │                 │                │
   │<──────────────────│                  │                 │                │
   │                   │                  │                 │                │
   │                   │                  │ Process command │                │
   │                   │                  │────────────────>│                │
   │                   │                  │                 │                │
   │                   │                  │                 │ Parse intent   │
   │                   │                  │                 │ Plan execution │
   │                   │                  │                 │                │
   │                   │                  │                 │ Execute CLI    │
   │                   │                  │                 │───────────────>│
   │                   │                  │                 │                │
   │                   │                  │                 │ gws calendar   │
   │                   │                  │                 │ +insert ...    │
   │                   │                  │                 │                │
   │                   │                  │                 │  CLI result    │
   │                   │                  │                 │<───────────────│
   │                   │                  │                 │                │
   │                   │                  │ Agent response  │                │
   │                   │                  │<────────────────│                │
   │                   │                  │                 │                │
   │                   │                  │ TTS Processing  │                │
   │                   │                  │                 │                │
   │                   │ Response + Audio │                 │                │
   │                   │<─────────────────│                 │                │
   │                   │                  │                 │                │
   │ Display message   │                  │                 │                │
   │ Play audio        │                  │                 │                │
   │<──────────────────│                  │                 │                │
   │                   │                  │                 │                │
   │ "Meeting scheduled│                  │                 │                │
   │  with John..."    │                  │                 │                │
   │<──────────────────│                  │                 │                │
```

### 6.2 Authentication Flow

```
┌──────┐       ┌──────────┐      ┌─────────┐      ┌────────┐      ┌───────────┐
│ User │       │Mobile App│      │ Backend │      │ Google │      │ Microsoft │
└──┬───┘       └────┬─────┘      └────┬────┘      └───┬────┘      └─────┬─────┘
   │                │                 │               │                  │
   │ Tap "Connect   │                 │               │                  │
   │ Google"        │                 │               │                  │
   │───────────────>│                 │               │                  │
   │                │                 │               │                  │
   │                │ Get OAuth URL   │               │                  │
   │                │────────────────>│               │                  │
   │                │                 │               │                  │
   │                │ OAuth URL       │               │                  │
   │                │<────────────────│               │                  │
   │                │                 │               │                  │
   │ Open browser   │                 │               │                  │
   │<───────────────│                 │               │                  │
   │                │                 │               │                  │
   │ Login & consent│                 │               │                  │
   │───────────────────────────────────────────────>│                  │
   │                │                 │               │                  │
   │ Redirect with  │                 │               │                  │
   │ auth code      │                 │               │                  │
   │<───────────────────────────────────────────────│                  │
   │                │                 │               │                  │
   │                │ Auth code       │               │                  │
   │                │────────────────>│               │                  │
   │                │                 │               │                  │
   │                │                 │ Exchange code │                  │
   │                │                 │──────────────>│                  │
   │                │                 │               │                  │
   │                │                 │ Tokens        │                  │
   │                │                 │<──────────────│                  │
   │                │                 │               │                  │
   │                │                 │ Store encrypted                  │
   │                │                 │ tokens        │                  │
   │                │                 │               │                  │
   │                │ Success         │               │                  │
   │                │<────────────────│               │                  │
   │                │                 │               │                  │
   │ "Google        │                 │               │                  │
   │  connected!"   │                 │               │                  │
   │<───────────────│                 │               │                  │
   │                │                 │               │                  │
   │ Tap "Connect   │                 │               │                  │
   │ Microsoft"     │                 │               │                  │
   │───────────────>│                 │               │                  │
   │                │                 │               │                  │
   │     ... similar flow for Microsoft ...          │                  │
   │                │                 │               │                  │
```

---

## 7. CLI Command Mapping

### 7.1 Google Workspace CLI (gws) Commands

| User Intent | Tool | Action | GWS Command |
|------------|------|--------|-------------|
| "Show my recent files" | google_drive | list | `gws drive files list --params '{"pageSize": 10, "orderBy": "modifiedTime desc"}'` |
| "Search for budget doc" | google_drive | search | `gws drive files list --params '{"q": "name contains 'budget'"}'` |
| "Upload report.pdf" | google_drive | upload | `gws +upload --file report.pdf` |
| "Share file with John" | google_drive | share | `gws drive permissions create --params '{"fileId": "...", "type": "user", "role": "reader", "emailAddress": "john@..."}'` |
| "Show unread emails" | google_gmail | list | `gws gmail users messages list --params '{"q": "is:unread", "maxResults": 10}'` |
| "Send email to boss" | google_gmail | send | `gws +send --to "boss@..." --subject "..." --body "..."` |
| "What's on my calendar" | google_calendar | agenda | `gws +agenda` |
| "Schedule meeting at 3pm" | google_calendar | create | `gws +insert --summary "..." --start "3pm" --attendees "..."` |
| "Read the sales spreadsheet" | google_sheets | read | `gws +read --spreadsheetId "..." --range "A1:D10"` |
| "Add row to expenses sheet" | google_sheets | append | `gws +append --spreadsheetId "..." --values '[["2024-01-15", "Lunch", "25"]]'` |
| "Create new document" | google_docs | create | `gws docs documents create --json '{"title": "..."}'` |
| "Post to team chat" | google_chat | send | `gws chat spaces messages create --params '{"parent": "spaces/...", "text": "..."}'` |

### 7.2 Microsoft 365 CLI (m365) Commands

| User Intent | Tool | Action | M365 Command |
|------------|------|--------|--------------|
| "List my Teams" | microsoft_teams | list | `m365 teams team list` |
| "Post to general channel" | microsoft_teams | post | `m365 teams message send --teamId "..." --channelId "..." --message "..."` |
| "Create Teams meeting" | microsoft_teams | meeting | `m365 teams meeting add --subject "..." --startTime "..." --endTime "..."` |
| "Show Outlook emails" | microsoft_outlook | list | `m365 outlook mail list` |
| "Send email via Outlook" | microsoft_outlook | send | `m365 outlook mail send --to "..." --subject "..." --bodyContents "..."` |
| "List calendar events" | microsoft_outlook | calendar | `m365 outlook event list` |
| "Create calendar event" | microsoft_outlook | create_event | `m365 outlook event add --subject "..." --startDateTime "..." --endDateTime "..."` |
| "Show OneDrive files" | microsoft_onedrive | list | `m365 onedrive list` |
| "Upload to OneDrive" | microsoft_onedrive | upload | `m365 file add --webUrl "..." --folder "..." --path "..."` |
| "List Planner tasks" | microsoft_planner | list | `m365 planner task list --planId "..."` |
| "Create Planner task" | microsoft_planner | create | `m365 planner task add --planId "..." --title "..." --bucketId "..."` |
| "Show my To Do tasks" | microsoft_todo | list | `m365 todo task list --listName "Tasks"` |
| "Add To Do item" | microsoft_todo | create | `m365 todo task add --listName "Tasks" --title "..."` |

---

## 8. Security Considerations

### 8.1 Authentication & Authorization

```python
# Security layers

1. User Authentication
   - JWT tokens with 1-hour expiry
   - Refresh tokens stored securely on device (Keychain/Keystore)
   - Biometric authentication option for app unlock

2. OAuth Token Management
   - Tokens encrypted at rest (AES-256)
   - Tokens never sent to client after initial auth
   - Automatic refresh before expiry
   - Scopes requested:
     * Google: gmail.modify, calendar, drive, sheets, docs, chat.messages
     * Microsoft: Mail.ReadWrite, Calendars.ReadWrite, Files.ReadWrite,
                  Team.ReadBasic.All, Tasks.ReadWrite

3. CLI Execution Security
   - Commands sanitized before execution
   - No shell injection possible (parameterized)
   - Audit log of all CLI executions
   - Rate limiting per user

4. Data Protection
   - All traffic over HTTPS/WSS
   - Voice data not stored after processing (ephemeral)
   - Conversation history encrypted
   - GDPR/CCPA compliant data handling
```

---

## 8.2 OAuth Flow & Credential Storage (DETAILED)

This section explains **how users connect their Google/Microsoft accounts** and how credentials are securely stored and used.

### 8.2.1 OAuth Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER ACCOUNT CONNECTION FLOW                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐      ┌──────────────┐      ┌─────────────┐      ┌───────────────┐
│  Mobile  │      │   Backend    │      │   Google/   │      │  Secure       │
│   App    │      │   Server     │      │  Microsoft  │      │  Storage      │
└────┬─────┘      └──────┬───────┘      └──────┬──────┘      └───────┬───────┘
     │                   │                     │                     │
     │ 1. User taps      │                     │                     │
     │ "Connect Google"  │                     │                     │
     │──────────────────>│                     │                     │
     │                   │                     │                     │
     │ 2. OAuth URL      │                     │                     │
     │<──────────────────│                     │                     │
     │                   │                     │                     │
     │ 3. Open browser   │                     │                     │
     │   for login       │                     │                     │
     │───────────────────────────────────────>│                     │
     │                   │                     │                     │
     │ 4. User logs in   │                     │                     │
     │   & grants access │                     │                     │
     │                   │                     │                     │
     │ 5. Redirect with  │                     │                     │
     │   auth code       │                     │                     │
     │<───────────────────────────────────────│                     │
     │                   │                     │                     │
     │ 6. Send auth code │                     │                     │
     │──────────────────>│                     │                     │
     │                   │                     │                     │
     │                   │ 7. Exchange code    │                     │
     │                   │   for tokens        │                     │
     │                   │────────────────────>│                     │
     │                   │                     │                     │
     │                   │ 8. Access token +   │                     │
     │                   │   Refresh token     │                     │
     │                   │<────────────────────│                     │
     │                   │                     │                     │
     │                   │ 9. Encrypt & store  │                     │
     │                   │   tokens            │                     │
     │                   │───────────────────────────────────────────>│
     │                   │                     │                     │
     │ 10. Success!      │                     │                     │
     │   Account linked  │                     │                     │
     │<──────────────────│                     │                     │
     │                   │                     │                     │
```

### 8.2.2 Mobile App - Account Connection UI

```typescript
// screens/AccountsScreen.tsx

import * as AuthSession from 'expo-auth-session';
import * as SecureStore from 'expo-secure-store';
import * as WebBrowser from 'expo-web-browser';

// ============================================
// CONNECTED ACCOUNTS SCREEN
// ============================================

const AccountsScreen: React.FC = () => {
  const { user, googleConnected, microsoftConnected } = useAuthStore();

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Connected Accounts</Text>
      <Text style={styles.subtitle}>
        Connect your workspace accounts to let Voice Agent manage your emails,
        calendar, files, and more.
      </Text>

      {/* Google Workspace Card */}
      <AccountCard
        provider="google"
        name="Google Workspace"
        description="Gmail, Calendar, Drive, Docs, Sheets"
        icon={<GoogleIcon />}
        connected={googleConnected}
        email={user?.googleEmail}
        onConnect={() => connectGoogle()}
        onDisconnect={() => disconnectGoogle()}
      />

      {/* Microsoft 365 Card */}
      <AccountCard
        provider="microsoft"
        name="Microsoft 365"
        description="Outlook, Teams, OneDrive, Planner, ToDo"
        icon={<MicrosoftIcon />}
        connected={microsoftConnected}
        email={user?.microsoftEmail}
        onConnect={() => connectMicrosoft()}
        onDisconnect={() => disconnectMicrosoft()}
      />

      {/* Permissions Info */}
      <PermissionsInfo />
    </SafeAreaView>
  );
};

// ============================================
// GOOGLE OAUTH CONFIGURATION
// ============================================

const GOOGLE_CONFIG = {
  clientId: process.env.GOOGLE_CLIENT_ID,
  scopes: [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/chat.messages',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
  ],
  redirectUri: AuthSession.makeRedirectUri({
    scheme: 'voiceagent',
    path: 'oauth/google',
  }),
};

const connectGoogle = async () => {
  try {
    // 1. Start OAuth flow
    const discovery = {
      authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
      tokenEndpoint: 'https://oauth2.googleapis.com/token',
      revocationEndpoint: 'https://oauth2.googleapis.com/revoke',
    };

    const authRequest = new AuthSession.AuthRequest({
      clientId: GOOGLE_CONFIG.clientId,
      scopes: GOOGLE_CONFIG.scopes,
      redirectUri: GOOGLE_CONFIG.redirectUri,
      usePKCE: true,  // Security: Use PKCE
      prompt: AuthSession.Prompt.Consent,
    });

    // 2. Open browser for user login
    const result = await authRequest.promptAsync(discovery);

    if (result.type === 'success') {
      // 3. Send auth code to backend
      const response = await api.post('/api/v1/auth/google/callback', {
        code: result.params.code,
        code_verifier: authRequest.codeVerifier,  // PKCE verifier
        redirect_uri: GOOGLE_CONFIG.redirectUri,
      });

      // 4. Store session token locally
      await SecureStore.setItemAsync('session_token', response.data.session_token);

      // 5. Update app state
      useAuthStore.getState().setGoogleConnected(true, response.data.email);

      Alert.alert('Success', 'Google Workspace connected!');
    }
  } catch (error) {
    Alert.alert('Error', 'Failed to connect Google account');
    console.error(error);
  }
};

// ============================================
// MICROSOFT OAUTH CONFIGURATION
// ============================================

const MICROSOFT_CONFIG = {
  clientId: process.env.MICROSOFT_CLIENT_ID,
  tenantId: 'common',  // Multi-tenant
  scopes: [
    'User.Read',
    'Mail.ReadWrite',
    'Calendars.ReadWrite',
    'Files.ReadWrite',
    'Team.ReadBasic.All',
    'Channel.ReadBasic.All',
    'Chat.ReadWrite',
    'Tasks.ReadWrite',
    'offline_access',  // For refresh token
  ],
  redirectUri: AuthSession.makeRedirectUri({
    scheme: 'voiceagent',
    path: 'oauth/microsoft',
  }),
};

const connectMicrosoft = async () => {
  try {
    const discovery = {
      authorizationEndpoint: `https://login.microsoftonline.com/${MICROSOFT_CONFIG.tenantId}/oauth2/v2.0/authorize`,
      tokenEndpoint: `https://login.microsoftonline.com/${MICROSOFT_CONFIG.tenantId}/oauth2/v2.0/token`,
    };

    const authRequest = new AuthSession.AuthRequest({
      clientId: MICROSOFT_CONFIG.clientId,
      scopes: MICROSOFT_CONFIG.scopes,
      redirectUri: MICROSOFT_CONFIG.redirectUri,
      usePKCE: true,
      prompt: AuthSession.Prompt.Consent,
    });

    const result = await authRequest.promptAsync(discovery);

    if (result.type === 'success') {
      const response = await api.post('/api/v1/auth/microsoft/callback', {
        code: result.params.code,
        code_verifier: authRequest.codeVerifier,
        redirect_uri: MICROSOFT_CONFIG.redirectUri,
      });

      await SecureStore.setItemAsync('session_token', response.data.session_token);
      useAuthStore.getState().setMicrosoftConnected(true, response.data.email);

      Alert.alert('Success', 'Microsoft 365 connected!');
    }
  } catch (error) {
    Alert.alert('Error', 'Failed to connect Microsoft account');
  }
};

// ============================================
// ACCOUNT CARD COMPONENT
// ============================================

const AccountCard: React.FC<{
  provider: 'google' | 'microsoft';
  name: string;
  description: string;
  icon: JSX.Element;
  connected: boolean;
  email?: string;
  onConnect: () => void;
  onDisconnect: () => void;
}> = ({ provider, name, description, icon, connected, email, onConnect, onDisconnect }) => (
  <View style={[styles.accountCard, connected && styles.accountCardConnected]}>
    <View style={styles.accountHeader}>
      <View style={styles.accountIcon}>{icon}</View>
      <View style={styles.accountInfo}>
        <Text style={styles.accountName}>{name}</Text>
        <Text style={styles.accountDescription}>{description}</Text>
      </View>
    </View>

    {connected ? (
      <View style={styles.connectedSection}>
        <View style={styles.connectedBadge}>
          <CheckCircleIcon color="#10B981" size={16} />
          <Text style={styles.connectedText}>Connected</Text>
        </View>
        <Text style={styles.connectedEmail}>{email}</Text>
        <TouchableOpacity onPress={onDisconnect} style={styles.disconnectButton}>
          <Text style={styles.disconnectText}>Disconnect</Text>
        </TouchableOpacity>
      </View>
    ) : (
      <TouchableOpacity onPress={onConnect} style={styles.connectButton}>
        <Text style={styles.connectButtonText}>Connect {name}</Text>
      </TouchableOpacity>
    )}
  </View>
);
```

### 8.2.3 Backend - OAuth Token Management

```python
# services/auth_service.py

from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import httpx
import jwt
from sqlalchemy.orm import Session

class OAuthService:
    """
    Handles OAuth token exchange, storage, and refresh for Google & Microsoft.
    Tokens are encrypted before storage and decrypted only when needed.
    """

    def __init__(self, db: Session, encryption_key: str):
        self.db = db
        self.cipher = Fernet(encryption_key.encode())

    # ============================================
    # GOOGLE OAUTH
    # ============================================

    async def exchange_google_code(
        self,
        code: str,
        code_verifier: str,
        redirect_uri: str,
        user_id: str
    ) -> dict:
        """Exchange Google auth code for tokens and store them."""

        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'code': code,
                    'code_verifier': code_verifier,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri,
                }
            )
            response.raise_for_status()
            tokens = response.json()

            # Get user info
            user_response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f"Bearer {tokens['access_token']}"}
            )
            user_info = user_response.json()

        # Encrypt and store tokens
        await self._store_oauth_credentials(
            user_id=user_id,
            provider='google',
            access_token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            expires_in=tokens.get('expires_in', 3600),
            scopes=tokens.get('scope', '').split(' '),
            email=user_info.get('email')
        )

        return {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
        }

    async def get_google_access_token(self, user_id: str) -> str:
        """Get valid Google access token, refreshing if needed."""

        creds = await self._get_oauth_credentials(user_id, 'google')
        if not creds:
            raise OAuthError("Google account not connected")

        # Check if token is expired (with 5 min buffer)
        if creds.token_expiry < datetime.utcnow() + timedelta(minutes=5):
            return await self._refresh_google_token(user_id, creds)

        return self._decrypt(creds.access_token_encrypted)

    async def _refresh_google_token(self, user_id: str, creds) -> str:
        """Refresh Google access token using refresh token."""

        refresh_token = self._decrypt(creds.refresh_token_encrypted)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token',
                }
            )
            response.raise_for_status()
            tokens = response.json()

        # Update stored tokens
        creds.access_token_encrypted = self._encrypt(tokens['access_token'])
        creds.token_expiry = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
        self.db.commit()

        return tokens['access_token']

    # ============================================
    # MICROSOFT OAUTH
    # ============================================

    async def exchange_microsoft_code(
        self,
        code: str,
        code_verifier: str,
        redirect_uri: str,
        user_id: str
    ) -> dict:
        """Exchange Microsoft auth code for tokens and store them."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                data={
                    'client_id': settings.MICROSOFT_CLIENT_ID,
                    'client_secret': settings.MICROSOFT_CLIENT_SECRET,
                    'code': code,
                    'code_verifier': code_verifier,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri,
                }
            )
            response.raise_for_status()
            tokens = response.json()

            # Get user info from Microsoft Graph
            user_response = await client.get(
                'https://graph.microsoft.com/v1.0/me',
                headers={'Authorization': f"Bearer {tokens['access_token']}"}
            )
            user_info = user_response.json()

        await self._store_oauth_credentials(
            user_id=user_id,
            provider='microsoft',
            access_token=tokens['access_token'],
            refresh_token=tokens.get('refresh_token'),
            expires_in=tokens.get('expires_in', 3600),
            scopes=tokens.get('scope', '').split(' '),
            email=user_info.get('mail') or user_info.get('userPrincipalName')
        )

        return {
            'email': user_info.get('mail') or user_info.get('userPrincipalName'),
            'name': user_info.get('displayName'),
        }

    async def get_microsoft_access_token(self, user_id: str) -> str:
        """Get valid Microsoft access token, refreshing if needed."""

        creds = await self._get_oauth_credentials(user_id, 'microsoft')
        if not creds:
            raise OAuthError("Microsoft account not connected")

        if creds.token_expiry < datetime.utcnow() + timedelta(minutes=5):
            return await self._refresh_microsoft_token(user_id, creds)

        return self._decrypt(creds.access_token_encrypted)

    async def _refresh_microsoft_token(self, user_id: str, creds) -> str:
        """Refresh Microsoft access token."""

        refresh_token = self._decrypt(creds.refresh_token_encrypted)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                data={
                    'client_id': settings.MICROSOFT_CLIENT_ID,
                    'client_secret': settings.MICROSOFT_CLIENT_SECRET,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token',
                }
            )
            response.raise_for_status()
            tokens = response.json()

        creds.access_token_encrypted = self._encrypt(tokens['access_token'])
        creds.token_expiry = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])

        # Microsoft may return a new refresh token
        if 'refresh_token' in tokens:
            creds.refresh_token_encrypted = self._encrypt(tokens['refresh_token'])

        self.db.commit()
        return tokens['access_token']

    # ============================================
    # TOKEN ENCRYPTION & STORAGE
    # ============================================

    def _encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data before storage."""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def _decrypt(self, ciphertext: str) -> str:
        """Decrypt sensitive data when needed."""
        return self.cipher.decrypt(ciphertext.encode()).decode()

    async def _store_oauth_credentials(
        self,
        user_id: str,
        provider: str,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        scopes: list,
        email: str
    ):
        """Store encrypted OAuth credentials in database."""

        # Check if credentials already exist
        existing = self.db.query(OAuthCredential).filter(
            OAuthCredential.user_id == user_id,
            OAuthCredential.provider == provider
        ).first()

        if existing:
            # Update existing
            existing.access_token_encrypted = self._encrypt(access_token)
            existing.refresh_token_encrypted = self._encrypt(refresh_token)
            existing.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            existing.scopes = scopes
            existing.email = email
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            creds = OAuthCredential(
                user_id=user_id,
                provider=provider,
                access_token_encrypted=self._encrypt(access_token),
                refresh_token_encrypted=self._encrypt(refresh_token),
                token_expiry=datetime.utcnow() + timedelta(seconds=expires_in),
                scopes=scopes,
                email=email
            )
            self.db.add(creds)

        self.db.commit()

    async def _get_oauth_credentials(self, user_id: str, provider: str):
        """Retrieve OAuth credentials for a user."""
        return self.db.query(OAuthCredential).filter(
            OAuthCredential.user_id == user_id,
            OAuthCredential.provider == provider
        ).first()

    async def revoke_credentials(self, user_id: str, provider: str):
        """Revoke and delete OAuth credentials."""

        creds = await self._get_oauth_credentials(user_id, provider)
        if not creds:
            return

        # Revoke token with provider
        access_token = self._decrypt(creds.access_token_encrypted)

        try:
            async with httpx.AsyncClient() as client:
                if provider == 'google':
                    await client.post(
                        'https://oauth2.googleapis.com/revoke',
                        params={'token': access_token}
                    )
                # Microsoft doesn't have a direct revoke endpoint
        except:
            pass  # Token may already be invalid

        # Delete from database
        self.db.delete(creds)
        self.db.commit()


class OAuthError(Exception):
    pass
```

### 8.2.4 Backend API Endpoints for Auth

```python
# api/auth.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class OAuthCallbackRequest(BaseModel):
    code: str
    code_verifier: str
    redirect_uri: str

class OAuthCallbackResponse(BaseModel):
    session_token: str
    email: str
    name: str

@router.get("/google/authorize")
async def google_authorize():
    """Get Google OAuth authorization URL (for web flow)."""
    return {
        "authorization_url": build_google_auth_url(),
        "state": generate_state_token()
    }

@router.post("/google/callback", response_model=OAuthCallbackResponse)
async def google_callback(
    request: OAuthCallbackRequest,
    user: User = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Handle Google OAuth callback.
    Exchange auth code for tokens and link to user account.
    """
    try:
        user_info = await oauth_service.exchange_google_code(
            code=request.code,
            code_verifier=request.code_verifier,
            redirect_uri=request.redirect_uri,
            user_id=str(user.id)
        )

        # Generate new session token
        session_token = create_session_token(user.id)

        return OAuthCallbackResponse(
            session_token=session_token,
            email=user_info['email'],
            name=user_info.get('name', '')
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")

@router.post("/microsoft/callback", response_model=OAuthCallbackResponse)
async def microsoft_callback(
    request: OAuthCallbackRequest,
    user: User = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Handle Microsoft OAuth callback."""
    try:
        user_info = await oauth_service.exchange_microsoft_code(
            code=request.code,
            code_verifier=request.code_verifier,
            redirect_uri=request.redirect_uri,
            user_id=str(user.id)
        )

        session_token = create_session_token(user.id)

        return OAuthCallbackResponse(
            session_token=session_token,
            email=user_info['email'],
            name=user_info.get('name', '')
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")

@router.delete("/google/disconnect")
async def disconnect_google(
    user: User = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Revoke and remove Google connection."""
    await oauth_service.revoke_credentials(str(user.id), 'google')
    return {"status": "disconnected"}

@router.delete("/microsoft/disconnect")
async def disconnect_microsoft(
    user: User = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Revoke and remove Microsoft connection."""
    await oauth_service.revoke_credentials(str(user.id), 'microsoft')
    return {"status": "disconnected"}

@router.get("/status")
async def auth_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authentication status for all providers."""
    google_creds = db.query(OAuthCredential).filter(
        OAuthCredential.user_id == str(user.id),
        OAuthCredential.provider == 'google'
    ).first()

    microsoft_creds = db.query(OAuthCredential).filter(
        OAuthCredential.user_id == str(user.id),
        OAuthCredential.provider == 'microsoft'
    ).first()

    return {
        "google": {
            "connected": google_creds is not None,
            "email": google_creds.email if google_creds else None,
            "scopes": google_creds.scopes if google_creds else [],
        },
        "microsoft": {
            "connected": microsoft_creds is not None,
            "email": microsoft_creds.email if microsoft_creds else None,
            "scopes": microsoft_creds.scopes if microsoft_creds else [],
        }
    }
```

### 8.2.5 How Tokens Flow to CLI Execution

```python
# agent/tools/base.py

class WorkspaceTool:
    """Base class for workspace tools that need OAuth tokens."""

    def __init__(self, user_id: str, oauth_service: OAuthService):
        self.user_id = user_id
        self.oauth_service = oauth_service

    async def get_google_token(self) -> str:
        """Get valid Google access token for CLI."""
        return await self.oauth_service.get_google_access_token(self.user_id)

    async def get_microsoft_token(self) -> str:
        """Get valid Microsoft access token for CLI."""
        return await self.oauth_service.get_microsoft_access_token(self.user_id)


# When executing CLI commands:

class GoogleCalendarTool(WorkspaceTool):

    async def _execute_gws(self, command: str) -> dict:
        """Execute gws CLI with user's token."""

        # Get fresh access token (auto-refreshed if needed)
        access_token = await self.get_google_token()

        result = subprocess.run(
            f"gws {command}",
            shell=True,
            capture_output=True,
            text=True,
            env={
                **os.environ,
                # Pass token to CLI via environment variable
                "GOOGLE_WORKSPACE_CLI_TOKEN": access_token
            }
        )
        return json.loads(result.stdout)
```

### 8.2.6 Credential Storage Summary

| Layer | What's Stored | How It's Protected |
|-------|---------------|-------------------|
| **Mobile App** | Session JWT only | Expo SecureStore (Keychain/Keystore) |
| **Backend DB** | Encrypted OAuth tokens | AES-256 (Fernet) encryption |
| **Redis Cache** | Short-lived access tokens | Auto-expire TTL |
| **CLI Execution** | Token in env var | Process-scoped, not persisted |

**Key Security Principles:**
1. **Tokens never leave backend** - Mobile app only has session JWT
2. **Encryption at rest** - All OAuth tokens encrypted in database
3. **Auto-refresh** - Tokens refreshed before expiry
4. **Minimal scope** - Only request permissions actually needed
5. **Revocation** - Users can disconnect anytime

---

### 8.3 Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| Chat messages | 60 | 1 minute |
| Voice STT | 30 | 1 minute |
| Voice TTS | 30 | 1 minute |
| CLI executions | 100 | 1 minute |
| OAuth refreshes | 10 | 1 hour |

---

## 9. Technology Stack

### 9.1 Mobile App
| Component | Technology | Why? |
|-----------|------------|------|
| Framework | React Native + Expo | Cross-platform iOS/Android, fast dev |
| UI Library | **assistant-ui** (React Native) | Claude-like chat UI, pre-built components |
| State Management | Zustand | Lightweight, simple, performant |
| Navigation | React Navigation (Drawer) | Native feel, thread management |
| Voice Recording | expo-av | Audio capture on both platforms |
| Wake Word | Picovoice Porcupine | Offline, low-power, custom keywords |
| Secure Storage | expo-secure-store | Keychain (iOS) / Keystore (Android) |
| WebSocket | React Native WebSocket | Real-time streaming |

**Quick Start:**
```bash
# Using assistant-ui LangGraph template for faster setup!
npx assistant-ui@latest create -t langgraph
```

### 9.2 Backend
| Component | Technology | Why? |
|-----------|------------|------|
| API Framework | **FastAPI** (Python) | Async, fast, auto-docs, WebSocket support |
| AI Framework | **LangGraph** + LangChain | Graph-based agents, tool calling, memory |
| LLM | Google Gemini 2.0 Flash | Fast, cheap, good tool calling |
| Voice TTS | Gemini 2.5 Flash TTS | 30 voices, natural speech |
| Voice STT | Gemini / Deepgram | Real-time transcription |
| Database | PostgreSQL | Reliable, JSONB support |
| Cache | Redis | Sessions, rate limiting |
| CLI Tools | `gws` (Google), `m365` (Microsoft) | Official workspace CLIs |

### 9.3 LangGraph vs Custom Agent (IMPORTANT!)

**We are NOT building our own agent framework!**

We use **LangGraph** which provides:
- ✅ Pre-built agent architecture
- ✅ Tool calling out of the box
- ✅ Memory & persistence built-in
- ✅ Streaming support
- ✅ Human-in-the-loop patterns

```python
# We USE LangGraph, not build from scratch!
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver

# Create agent with tools (our CLI wrappers)
agent = create_react_agent(
    model=gemini_model,
    tools=[google_drive, google_gmail, google_calendar, ms_teams, ...],
    checkpointer=PostgresSaver(db_connection)  # Built-in persistence!
)
```

### 9.4 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HOW EVERYTHING CONNECTS                               │
└─────────────────────────────────────────────────────────────────────────────┘

MOBILE APP (React Native + Expo)
    │
    │  Uses: assistant-ui LangGraph template
    │  - Already has WebSocket setup for LangGraph
    │  - Streaming responses built-in
    │  - Tool call display built-in
    │
    │  npx assistant-ui@latest create -t langgraph
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ASSISTANT-UI RUNTIME                                                        │
│  - Connects to backend via WebSocket/REST                                   │
│  - Handles streaming automatically                                          │
│  - Renders tool calls with status                                           │
│  - Manages conversation state                                               │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    │ WebSocket: wss://api.voiceagent.app/ws/chat
    │ REST: https://api.voiceagent.app/api/v1/*
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  FASTAPI BACKEND                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ /api/v1/chat (POST)        → LangGraph agent.invoke()                 │  │
│  │ /ws/chat (WebSocket)       → LangGraph agent.astream()                │  │
│  │ /api/v1/voice/stt (POST)   → Gemini multimodal transcription          │  │
│  │ /api/v1/voice/tts (POST)   → Gemini TTS                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    │ LangGraph handles:
    │ - Intent understanding
    │ - Tool selection
    │ - Memory management
    │ - Response generation
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LANGGRAPH AGENT                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Model: Gemini 2.0 Flash                                               │  │
│  │                                                                        │  │
│  │ Tools (our custom wrappers):                                          │  │
│  │ ├── GoogleDriveTool      → executes `gws drive ...`                   │  │
│  │ ├── GoogleGmailTool      → executes `gws gmail ...` / `gws +send`     │  │
│  │ ├── GoogleCalendarTool   → executes `gws calendar ...` / `gws +agenda`│  │
│  │ ├── GoogleSheetsTool     → executes `gws sheets ...`                  │  │
│  │ ├── MicrosoftTeamsTool   → executes `m365 teams ...`                  │  │
│  │ ├── MicrosoftOutlookTool → executes `m365 outlook ...`                │  │
│  │ └── ... more tools                                                    │  │
│  │                                                                        │  │
│  │ Checkpointer: PostgresSaver (conversation persistence)                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    │ Tools execute CLI commands
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLI LAYER                                                                   │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│  │ Google Workspace CLI (gws)   │  │ Microsoft 365 CLI (m365)     │        │
│  │                              │  │                              │        │
│  │ Auth: OAuth access token     │  │ Auth: OAuth access token     │        │
│  │ passed via env var           │  │ passed via env var           │        │
│  │                              │  │                              │        │
│  │ GOOGLE_WORKSPACE_CLI_TOKEN   │  │ CLIMICROSOFT365_ACCESSTOKEN  │        │
│  └──────────────────────────────┘  └──────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  GOOGLE WORKSPACE / MICROSOFT 365 APIS                                       │
│  - Gmail, Calendar, Drive, Docs, Sheets, Chat                               │
│  - Teams, Outlook, OneDrive, Planner, ToDo, SharePoint                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.5 Infrastructure
| Component | Technology |
|-----------|------------|
| Cloud | GCP (recommended - Gemini native) |
| Container | Docker + Cloud Run |
| CI/CD | GitHub Actions |
| Monitoring | Google Cloud Monitoring |
| Logging | Cloud Logging |

---

## 10. Project Structure

```
voice-ai-agent/
├── mobile/                          # React Native app
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatScreen.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── ComposerBar.tsx
│   │   │   │   ├── ToolCallDisplay.tsx
│   │   │   │   └── VoiceOverlay.tsx
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   └── Loading.tsx
│   │   │   └── settings/
│   │   │       ├── SettingsScreen.tsx
│   │   │       └── AccountScreen.tsx
│   │   ├── services/
│   │   │   ├── WakeWordService.ts
│   │   │   ├── VoiceIOManager.ts
│   │   │   ├── ApiService.ts
│   │   │   ├── WebSocketService.ts
│   │   │   └── AuthService.ts
│   │   ├── store/
│   │   │   ├── appStore.ts
│   │   │   ├── authStore.ts
│   │   │   └── settingsStore.ts
│   │   ├── hooks/
│   │   │   ├── useVoice.ts
│   │   │   ├── useChat.ts
│   │   │   └── useAuth.ts
│   │   ├── navigation/
│   │   │   ├── AppNavigator.tsx
│   │   │   └── AuthNavigator.tsx
│   │   ├── utils/
│   │   │   ├── audio.ts
│   │   │   └── formatting.ts
│   │   └── types/
│   │       └── index.ts
│   ├── app.json
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                         # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── voice.py
│   │   │   ├── conversations.py
│   │   │   ├── auth.py
│   │   │   └── websocket.py
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── core.py              # Main AI agent
│   │   │   ├── prompts.py           # System prompts
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── base.py
│   │   │       ├── google_workspace.py
│   │   │       └── microsoft365.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── voice_service.py     # Gemini TTS/STT
│   │   │   ├── cli_executor.py      # CLI execution
│   │   │   └── auth_service.py      # OAuth handling
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   └── message.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── redis.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_agent.py
│   │   ├── test_tools.py
│   │   └── test_api.py
│   ├── alembic/                     # DB migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/
│   ├── LLD-Voice-AI-Agent.md        # This document
│   ├── API.md
│   └── DEPLOYMENT.md
│
└── README.md
```

---

## 11. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure (mobile + backend)
- [ ] Implement basic FastAPI backend with auth
- [ ] Set up PostgreSQL + Redis
- [ ] Implement Google OAuth flow
- [ ] Implement Microsoft OAuth flow
- [ ] Basic React Native app with navigation

### Phase 2: Core Agent (Week 3-4)
- [ ] Implement LangChain agent with Gemini
- [ ] Build Google Workspace tools (Drive, Gmail, Calendar)
- [ ] Build Microsoft 365 tools (Teams, Outlook, OneDrive)
- [ ] Chat API endpoint with tool execution
- [ ] WebSocket for streaming responses

### Phase 3: Voice Integration (Week 5-6)
- [ ] Integrate Gemini STT
- [ ] Integrate Gemini TTS
- [ ] Voice recording in mobile app
- [ ] Audio playback for responses
- [ ] Wake word detection (Porcupine)

### Phase 4: Chat UI (Week 7-8)
- [ ] Integrate assistant-ui components
- [ ] Conversation list & history
- [ ] Message display with tool calls
- [ ] Voice input UI overlay
- [ ] Settings screen

### Phase 5: Polish & Testing (Week 9-10)
- [ ] Error handling & edge cases
- [ ] Performance optimization
- [ ] Security audit
- [ ] User testing
- [ ] Bug fixes

---

## 12. Open Questions / Decisions Needed

1. **App Name / Wake Word**: What should the wake word be? (e.g., "Hey Agent", "OK Jarvis", custom?)

2. **Voice Selection**: Which Gemini voice should be default? (Kore is friendly, Charon is professional)

3. **Offline Support**: Should basic commands work offline? (adds complexity)

4. **Multi-language**: Priority for non-English language support?

5. **Team Features**: Should multiple users share workspace context? (enterprise feature)

6. **Billing Model**: Free tier limits? Premium features?

---

*Document Version: 1.0*
*Last Updated: 2024-01-15*
*Author: Voice AI Agent Team*
