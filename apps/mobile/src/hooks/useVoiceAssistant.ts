import { useEffect, useRef } from "react";
import { Audio, InterruptionModeAndroid, InterruptionModeIOS } from "expo-av";
import * as Speech from "expo-speech";
import { useShallow } from "zustand/react/shallow";

import { currentUserId } from "../config";
import {
  confirmApproval,
  rejectApproval,
  sendChatMessage,
  transcribeAudio,
} from "../services/api";
import { getIdleVoiceState, useChatStore } from "../store/chatStore";


const DEFAULT_VOICE_COMMAND = "Show my calendar today";
const FOLLOWUP_WINDOW_SECONDS = 5;
const MAX_CAPTURE_MILLIS = 9_000;
const MIN_RECORDING_MILLIS = 350;
const STOP_COMMANDS = new Set(["stop", "cancel", "never mind", "stop listening"]);

function createMessage(role: "user" | "assistant", text: string) {
  return {
    id: `${role}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    role,
    text,
    createdAt: new Date().toISOString(),
  };
}

function buildAcknowledgement(message: string): string {
  const lowered = message.toLowerCase();

  if (/(send|email|post|share|schedule|create|delete|update)/.test(lowered)) {
    return "Got it. I will let you know if approval is needed.";
  }

  if (/(show|list|find|search|calendar|drive|files|onedrive|read)/.test(lowered)) {
    return "Checking that.";
  }

  return "Got it.";
}

function buildSpokenSummary(reply: string, approvalNeeded: boolean): string {
  if (approvalNeeded) {
    return "I need approval before completing that.";
  }

  const firstSentence = reply
    .split(/(?<=[.!?])\s+/)
    .map((part) => part.trim())
    .find(Boolean);

  if (!firstSentence) {
    return "Done.";
  }

  return firstSentence.length > 120 ? `${firstSentence.slice(0, 117).trim()}...` : firstSentence;
}

export function useVoiceAssistant() {
  const {
    approval,
    backgroundListeningEnabled,
    pushMessage,
    setApproval,
    setBackgroundListeningEnabled,
    setFollowupSecondsRemaining,
    setLastCapturedCommand,
    setLastSpokenSummary,
    setVoiceState,
    threadId,
    voiceState,
  } = useChatStore(
    useShallow((state) => ({
      approval: state.approval,
      backgroundListeningEnabled: state.backgroundListeningEnabled,
      pushMessage: state.pushMessage,
      setApproval: state.setApproval,
      setBackgroundListeningEnabled: state.setBackgroundListeningEnabled,
      setFollowupSecondsRemaining: state.setFollowupSecondsRemaining,
      setLastCapturedCommand: state.setLastCapturedCommand,
      setLastSpokenSummary: state.setLastSpokenSummary,
      setVoiceState: state.setVoiceState,
      threadId: state.threadId,
      voiceState: state.voiceState,
    })),
  );

  const followupIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const wakeWordTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const captureTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const recordingRef = useRef<Audio.Recording | null>(null);
  const speechTokenRef = useRef(0);

  const resetToIdle = () => {
    setFollowupSecondsRemaining(0);
    setVoiceState(getIdleVoiceState(backgroundListeningEnabled));
  };

  const clearFollowupWindow = () => {
    if (followupIntervalRef.current) {
      clearInterval(followupIntervalRef.current);
      followupIntervalRef.current = null;
    }
    setFollowupSecondsRemaining(0);
  };

  const clearWakeWordTimeout = () => {
    if (wakeWordTimeoutRef.current) {
      clearTimeout(wakeWordTimeoutRef.current);
      wakeWordTimeoutRef.current = null;
    }
  };

  const clearCaptureTimeout = () => {
    if (captureTimeoutRef.current) {
      clearTimeout(captureTimeoutRef.current);
      captureTimeoutRef.current = null;
    }
  };

  const invalidateSpeechCallbacks = () => {
    speechTokenRef.current += 1;
  };

  const stopSpeechOutput = () => {
    invalidateSpeechCallbacks();
    Speech.stop();
  };

  const configureAudioForRecording = async () => {
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      interruptionModeIOS: InterruptionModeIOS.DoNotMix,
      playsInSilentModeIOS: true,
      staysActiveInBackground: backgroundListeningEnabled,
      interruptionModeAndroid: InterruptionModeAndroid.DoNotMix,
      shouldDuckAndroid: false,
      playThroughEarpieceAndroid: false,
    });
  };

  const configureAudioForPlayback = async () => {
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
      interruptionModeIOS: InterruptionModeIOS.DuckOthers,
      playsInSilentModeIOS: true,
      staysActiveInBackground: backgroundListeningEnabled,
      interruptionModeAndroid: InterruptionModeAndroid.DuckOthers,
      shouldDuckAndroid: true,
      playThroughEarpieceAndroid: false,
    });
  };

  const beginFollowupWindow = () => {
    clearFollowupWindow();
    setVoiceState("followup_listening");
    setFollowupSecondsRemaining(FOLLOWUP_WINDOW_SECONDS);

    let remaining = FOLLOWUP_WINDOW_SECONDS;
    followupIntervalRef.current = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearFollowupWindow();
        resetToIdle();
        return;
      }
      setFollowupSecondsRemaining(remaining);
    }, 1000);
  };

  const speakText = (text: string, onDone?: () => void) => {
    const token = speechTokenRef.current + 1;
    speechTokenRef.current = token;
    setLastSpokenSummary(text);
    setVoiceState("speaking_result");
    Speech.stop();

    let settled = false;
    const finish = () => {
      if (settled || speechTokenRef.current !== token) {
        return;
      }
      settled = true;
      onDone?.();
    };

    Speech.speak(text, {
      rate: 1,
      onDone: finish,
      onStopped: finish,
      onError: finish,
    });
  };

  const surfaceVoiceRecovery = (text: string, followup = true) => {
    pushMessage(createMessage("assistant", text));
    setVoiceState("error_recovery");
    speakText(text, () => {
      if (followup) {
        beginFollowupWindow();
        return;
      }
      resetToIdle();
    });
  };

  const handleStopIntent = async (message: string, source: "text" | "voice") => {
    pushMessage(createMessage("user", message));
    clearFollowupWindow();
    clearWakeWordTimeout();
    clearCaptureTimeout();
    stopSpeechOutput();
    setApproval(null);
    pushMessage(createMessage("assistant", "Okay, stopping."));
    setLastCapturedCommand(message);

    if (source === "voice") {
      speakText("Okay, stopping.", () => {
        resetToIdle();
      });
      return;
    }

    resetToIdle();
  };

  const submitTurn = async (rawMessage: string, source: "text" | "voice"): Promise<void> => {
    const message = rawMessage.trim() || DEFAULT_VOICE_COMMAND;
    const normalized = message.toLowerCase();

    if (STOP_COMMANDS.has(normalized)) {
      await handleStopIntent(message, source);
      return;
    }

    clearFollowupWindow();
    setLastCapturedCommand(message);
    pushMessage(createMessage("user", message));

    if (source === "voice") {
      setVoiceState("processing_turn");
      const acknowledgement = buildAcknowledgement(message);
      setLastSpokenSummary(acknowledgement);
      stopSpeechOutput();
      Speech.speak(acknowledgement, { rate: 1 });
    } else {
      setLastSpokenSummary(null);
    }

    setVoiceState("executing_task");

    try {
      const result = await sendChatMessage({
        thread_id: threadId,
        user_id: currentUserId,
        message,
        input_mode: source,
      });

      pushMessage(createMessage("assistant", result.reply));

      if (result.approval) {
        setApproval({
          approvalId: result.approval.approval_id,
          actionSummary: result.approval.action_summary,
          toolName: result.approval.tool_name,
        });

        if (source === "voice") {
          speakText("I need approval before completing that.", () => {
            setVoiceState("awaiting_approval");
          });
        } else {
          setVoiceState("awaiting_approval");
        }
        return;
      }

      setApproval(null);

      if (source === "voice") {
        speakText(buildSpokenSummary(result.reply, false), () => {
          beginFollowupWindow();
        });
      } else {
        resetToIdle();
      }
    } catch (error) {
      const detail =
        error instanceof Error ? error.message : "I ran into a problem while processing that request.";
      pushMessage(createMessage("assistant", detail));
      setVoiceState("error_recovery");

      if (source === "voice") {
        speakText("I ran into a problem. Please try again.", () => {
          resetToIdle();
        });
        return;
      }

      resetToIdle();
    }
  };

  const cancelActiveRecording = async () => {
    const recording = recordingRef.current;
    recordingRef.current = null;
    clearCaptureTimeout();

    if (!recording) {
      await configureAudioForPlayback().catch(() => undefined);
      return false;
    }

    try {
      await recording.stopAndUnloadAsync();
    } catch {
      // Ignore cancellation failures from partially-started recordings.
    } finally {
      await configureAudioForPlayback().catch(() => undefined);
    }

    return true;
  };

  const beginVoiceCapture = async () => {
    clearFollowupWindow();
    clearWakeWordTimeout();
    clearCaptureTimeout();
    stopSpeechOutput();

    const permission = await Audio.requestPermissionsAsync();
    if (!permission.granted) {
      surfaceVoiceRecovery("Microphone access is required before I can listen.");
      return;
    }

    try {
      await configureAudioForRecording();
      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await recording.startAsync();
      recordingRef.current = recording;
      setVoiceState("capturing_command");
      captureTimeoutRef.current = setTimeout(() => {
        void finishVoiceCapture();
      }, MAX_CAPTURE_MILLIS);
    } catch (error) {
      const detail =
        error instanceof Error ? error.message : "I could not start the microphone capture.";
      surfaceVoiceRecovery(detail, false);
    }
  };

  const finishVoiceCapture = async () => {
    clearWakeWordTimeout();
    clearCaptureTimeout();

    const recording = recordingRef.current;
    recordingRef.current = null;

    if (!recording) {
      resetToIdle();
      return;
    }

    setVoiceState("processing_turn");

    let durationMillis = 0;
    let uri: string | null = null;

    try {
      const status = await recording.stopAndUnloadAsync();
      durationMillis = status.durationMillis ?? 0;
      uri = recording.getURI();
    } catch {
      await configureAudioForPlayback().catch(() => undefined);
      surfaceVoiceRecovery("I did not catch that. Please try again.");
      return;
    }

    await configureAudioForPlayback().catch(() => undefined);

    if (!uri || durationMillis < MIN_RECORDING_MILLIS) {
      surfaceVoiceRecovery("I did not catch that. Please try again.");
      return;
    }

    try {
      const transcription = await transcribeAudio(uri);
      const transcript = transcription.text.trim();

      if (!transcript) {
        surfaceVoiceRecovery("I did not catch a clear command. Please try again.");
        return;
      }

      await submitTurn(transcript, "voice");
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Voice transcription failed.";
      surfaceVoiceRecovery(detail);
    }
  };

  const triggerWakeWord = async (message?: string) => {
    if (!["idle_passive", "followup_listening", "hold_ready", "error_recovery"].includes(voiceState)) {
      return;
    }

    clearFollowupWindow();
    clearWakeWordTimeout();
    stopSpeechOutput();
    setVoiceState("wake_detected");

    wakeWordTimeoutRef.current = setTimeout(() => {
      const simulatedTranscript = message?.trim();
      if (simulatedTranscript) {
        void submitTurn(simulatedTranscript, "voice");
        return;
      }
      void beginVoiceCapture();
    }, 220);
  };

  const startHoldToTalk = async () => {
    if (!["hold_ready", "followup_listening", "idle_passive", "error_recovery"].includes(voiceState)) {
      return;
    }

    await beginVoiceCapture();
  };

  const finishHoldToTalk = async () => {
    if (voiceState !== "capturing_command") {
      return;
    }

    await finishVoiceCapture();
  };

  const submitTextTurn = async (message: string) => {
    await submitTurn(message, "text");
  };

  const approvePendingAction = async () => {
    if (!approval) {
      return;
    }

    clearFollowupWindow();
    setVoiceState("executing_task");

    try {
      const result = await confirmApproval(approval.approvalId);
      pushMessage(createMessage("assistant", result.message));
      setApproval(null);
      speakText(buildSpokenSummary(result.message, false), () => {
        beginFollowupWindow();
      });
    } catch (error) {
      const detail = error instanceof Error ? error.message : "The approval could not be completed.";
      pushMessage(createMessage("assistant", detail));
      setVoiceState("error_recovery");
      speakText("I could not complete that approval.", () => {
        resetToIdle();
      });
    }
  };

  const rejectPendingAction = async () => {
    if (!approval) {
      return;
    }

    clearFollowupWindow();
    setVoiceState("executing_task");

    try {
      const result = await rejectApproval(approval.approvalId);
      pushMessage(createMessage("assistant", result.message));
      setApproval(null);
      speakText(buildSpokenSummary(result.message, false), () => {
        beginFollowupWindow();
      });
    } catch (error) {
      const detail = error instanceof Error ? error.message : "The approval could not be rejected.";
      pushMessage(createMessage("assistant", detail));
      setVoiceState("error_recovery");
      speakText("I could not reject that approval.", () => {
        resetToIdle();
      });
    }
  };

  const stopListening = async () => {
    clearFollowupWindow();
    clearWakeWordTimeout();
    stopSpeechOutput();

    if (voiceState === "capturing_command") {
      await finishVoiceCapture();
      return;
    }

    await cancelActiveRecording();
    setLastSpokenSummary("Stopped listening.");
    resetToIdle();
  };

  const toggleBackgroundListening = (enabled: boolean) => {
    clearFollowupWindow();
    setBackgroundListeningEnabled(enabled);
    setLastSpokenSummary(
      enabled ? "Background listening armed." : "Background listening turned off.",
    );
    setVoiceState(getIdleVoiceState(enabled));
  };

  useEffect(() => {
    return () => {
      clearFollowupWindow();
      clearWakeWordTimeout();
      clearCaptureTimeout();
      void cancelActiveRecording();
      stopSpeechOutput();
    };
  }, []);

  const canStartVoiceTurn = ["hold_ready", "idle_passive", "followup_listening", "error_recovery"].includes(voiceState);
  const canChangeListeningMode = ["hold_ready", "idle_passive", "followup_listening", "error_recovery"].includes(voiceState);

  return {
    approval,
    canChangeListeningMode,
    canStartVoiceTurn,
    canTriggerWakeWord: canStartVoiceTurn,
    followupWindowActive: voiceState === "followup_listening",
    submitTextTurn,
    startHoldToTalk,
    finishHoldToTalk,
    triggerWakeWord,
    approvePendingAction,
    rejectPendingAction,
    stopListening,
    toggleBackgroundListening,
  };
}
