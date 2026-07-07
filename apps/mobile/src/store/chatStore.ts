import { create } from "zustand";


export type VoiceState =
  | "hold_ready"
  | "idle_passive"
  | "wake_detected"
  | "capturing_command"
  | "processing_turn"
  | "executing_task"
  | "awaiting_approval"
  | "speaking_result"
  | "followup_listening"
  | "error_recovery";

export type AppMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  createdAt: string;
};

export type ApprovalState = {
  approvalId: string;
  actionSummary: string;
  toolName: string;
} | null;

type ChatState = {
  threadId: string;
  messages: AppMessage[];
  voiceState: VoiceState;
  approval: ApprovalState;
  backgroundListeningEnabled: boolean;
  followupSecondsRemaining: number;
  lastCapturedCommand: string | null;
  lastSpokenSummary: string | null;
  setVoiceState: (state: VoiceState) => void;
  pushMessage: (message: AppMessage) => void;
  setApproval: (approval: ApprovalState) => void;
  setBackgroundListeningEnabled: (enabled: boolean) => void;
  setFollowupSecondsRemaining: (seconds: number) => void;
  setLastCapturedCommand: (command: string | null) => void;
  setLastSpokenSummary: (summary: string | null) => void;
};

export function getIdleVoiceState(backgroundListeningEnabled: boolean): VoiceState {
  return backgroundListeningEnabled ? "idle_passive" : "hold_ready";
}

export const useChatStore = create<ChatState>((set) => ({
  threadId: "thread_mobile_demo",
  messages: [
    {
      id: "welcome",
      role: "assistant",
      text: "Wake me with your trigger word or use hold-to-talk. I can read calendars, search files, and pause for approvals before write actions.",
      createdAt: new Date().toISOString(),
    },
  ],
  voiceState: "hold_ready",
  approval: null,
  backgroundListeningEnabled: false,
  followupSecondsRemaining: 0,
  lastCapturedCommand: null,
  lastSpokenSummary: null,
  setVoiceState: (voiceState) => set({ voiceState }),
  pushMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setApproval: (approval) => set({ approval }),
  setBackgroundListeningEnabled: (backgroundListeningEnabled) =>
    set((state) => ({
      backgroundListeningEnabled,
      voiceState:
        state.voiceState === "hold_ready" ||
        state.voiceState === "idle_passive" ||
        state.voiceState === "followup_listening"
          ? getIdleVoiceState(backgroundListeningEnabled)
          : state.voiceState,
    })),
  setFollowupSecondsRemaining: (followupSecondsRemaining) =>
    set({ followupSecondsRemaining }),
  setLastCapturedCommand: (lastCapturedCommand) => set({ lastCapturedCommand }),
  setLastSpokenSummary: (lastSpokenSummary) => set({ lastSpokenSummary }),
}));
