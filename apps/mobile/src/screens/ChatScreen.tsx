import React, { useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from "react-native";
import { useShallow } from "zustand/react/shallow";

import { ApprovalCard } from "../components/ApprovalCard";
import { HoldToTalkButton } from "../components/HoldToTalkButton";
import { MessageBubble } from "../components/MessageBubble";
import { useVoiceAssistant } from "../hooks/useVoiceAssistant";
import { VoiceStatusPill } from "../components/VoiceStatusPill";
import { useChatStore } from "../store/chatStore";
import { colors, radius, spacing } from "../theme/tokens";


const SAMPLE_COMMANDS = [
  "Show my calendar today",
  "Find the latest budget spreadsheet",
  "Send the project update to the team",
];

function buildModeSummary(backgroundListeningEnabled: boolean, followupSecondsRemaining: number) {
  if (followupSecondsRemaining > 0) {
    return `Waiting ${followupSecondsRemaining}s for a follow-up without needing the wake word again.`;
  }

  return backgroundListeningEnabled
    ? "Wake-word listening is armed. Trigger the wake word to capture the next spoken command."
    : "Hold-to-talk is active. You can arm background listening when you want hands-free use.";
}

function getSecondaryActionLabel(voiceState: string) {
  if (voiceState === "capturing_command") {
    return "Finish Capture";
  }

  if (voiceState === "wake_detected") {
    return "Cancel";
  }

  return "Stop";
}

export function ChatScreen() {
  const [draft, setDraft] = useState("");
  const {
    approval,
    backgroundListeningEnabled,
    followupSecondsRemaining,
    lastCapturedCommand,
    lastSpokenSummary,
    messages,
    voiceState,
  } = useChatStore(
    useShallow((state) => ({
      approval: state.approval,
      backgroundListeningEnabled: state.backgroundListeningEnabled,
      followupSecondsRemaining: state.followupSecondsRemaining,
      lastCapturedCommand: state.lastCapturedCommand,
      lastSpokenSummary: state.lastSpokenSummary,
      messages: state.messages,
      voiceState: state.voiceState,
    })),
  );
  const voice = useVoiceAssistant();
  const composerDisabled = [
    "wake_detected",
    "capturing_command",
    "processing_turn",
    "executing_task",
    "awaiting_approval",
    "speaking_result",
  ].includes(voiceState);

  const handleSend = async () => {
    const trimmed = draft.trim();
    if (!trimmed) {
      return;
    }

    setDraft("");
    await voice.submitTextTurn(trimmed);
  };

  const handleTriggerWakeWord = () => {
    void voice.triggerWakeWord();
  };

  const handleQuickAction = (command: string) => {
    if (backgroundListeningEnabled) {
      void voice.triggerWakeWord(command);
      return;
    }

    void voice.submitTextTurn(command);
  };

  const canTriggerWakeWord = backgroundListeningEnabled && voice.canTriggerWakeWord;
  const secondaryActionLabel = getSecondaryActionLabel(voiceState);

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.container}
    >
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Voice Agent</Text>
          <Text style={styles.subtitle}>Wake-word workspace assistant for Google and Microsoft</Text>
        </View>
        <VoiceStatusPill state={voiceState} />
      </View>

      <View style={styles.voiceCard}>
        <View style={styles.voiceCardHeader}>
          <View style={styles.voiceCopy}>
            <Text style={styles.voiceTitle}>Listening Mode</Text>
            <Text style={styles.voiceBody}>
              {buildModeSummary(backgroundListeningEnabled, followupSecondsRemaining)}
            </Text>
          </View>
          <Switch
            value={backgroundListeningEnabled}
            disabled={!voice.canChangeListeningMode}
            onValueChange={voice.toggleBackgroundListening}
            trackColor={{ false: colors.surfaceMuted, true: colors.accentSoft }}
            thumbColor={backgroundListeningEnabled ? colors.accent : colors.surface}
          />
        </View>

        {lastCapturedCommand ? (
          <Text style={styles.metaLine}>Last captured command: {lastCapturedCommand}</Text>
        ) : null}
        {lastSpokenSummary ? (
          <Text style={styles.metaLine}>Last spoken summary: {lastSpokenSummary}</Text>
        ) : null}

        <View style={styles.voiceActions}>
          <Pressable
            disabled={!canTriggerWakeWord}
            style={[
              styles.secondaryAction,
              canTriggerWakeWord ? styles.secondaryActionActive : styles.secondaryActionDisabled,
            ]}
            onPress={handleTriggerWakeWord}
          >
            <Text style={styles.secondaryActionLabel}>Trigger Wake Word</Text>
          </Pressable>
          <Pressable style={styles.ghostAction} onPress={() => void voice.stopListening()}>
            <Text style={styles.ghostActionLabel}>{secondaryActionLabel}</Text>
          </Pressable>
        </View>

        <View style={styles.quickActions}>
          {SAMPLE_COMMANDS.map((command) => (
            <Pressable
              key={command}
              style={styles.quickChip}
              disabled={composerDisabled}
              onPress={() => handleQuickAction(command)}
            >
              <Text style={styles.quickChipLabel}>{command}</Text>
            </Pressable>
          ))}
        </View>
      </View>

      <View style={styles.threadShell}>
        <ScrollView contentContainerStyle={styles.threadContent}>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {approval ? (
            <ApprovalCard
              title={approval.actionSummary}
              toolName={approval.toolName}
              onApprove={() => void voice.approvePendingAction()}
              onReject={() => void voice.rejectPendingAction()}
            />
          ) : null}
        </ScrollView>
      </View>

      <View style={styles.composerShell}>
        <TextInput
          style={styles.input}
          placeholder="Type a message or use the mic for a spoken command"
          placeholderTextColor={colors.textMuted}
          value={draft}
          editable={!composerDisabled}
          onChangeText={setDraft}
        />
        <Pressable
          disabled={composerDisabled}
          style={[styles.sendButton, composerDisabled ? styles.sendButtonDisabled : null]}
          onPress={() => void handleSend()}
        >
          <Text style={styles.sendLabel}>Send</Text>
        </Pressable>
      </View>

      <HoldToTalkButton
        disabled={!voice.canStartVoiceTurn}
        state={voiceState}
        onPressIn={() => void voice.startHoldToTalk()}
        onPressOut={() => {
          void voice.finishHoldToTalk();
        }}
      />
    </KeyboardAvoidingView>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    paddingBottom: spacing.lg,
  },
  header: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
    gap: spacing.md,
  },
  title: {
    color: colors.text,
    fontSize: 28,
    fontWeight: "700",
  },
  subtitle: {
    color: colors.textMuted,
    fontSize: 14,
    marginTop: spacing.xs,
  },
  voiceCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  voiceCardHeader: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  voiceCopy: {
    flex: 1,
  },
  voiceTitle: {
    color: colors.text,
    fontWeight: "700",
    fontSize: 18,
  },
  voiceBody: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 20,
    marginTop: spacing.xs,
  },
  metaLine: {
    color: colors.textMuted,
    fontSize: 13,
    lineHeight: 18,
    marginTop: spacing.md,
  },
  voiceActions: {
    flexDirection: "row",
    gap: spacing.md,
    marginTop: spacing.lg,
  },
  secondaryAction: {
    flex: 1,
    minHeight: 46,
    borderRadius: radius.pill,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
  },
  secondaryActionActive: {
    borderColor: colors.accent,
    backgroundColor: colors.accentSoft,
  },
  secondaryActionDisabled: {
    borderColor: colors.border,
    backgroundColor: colors.surfaceMuted,
  },
  secondaryActionLabel: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "700",
  },
  ghostAction: {
    minWidth: 88,
    minHeight: 46,
    borderRadius: radius.pill,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surfaceMuted,
  },
  ghostActionLabel: {
    color: colors.text,
    fontWeight: "600",
  },
  quickActions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  quickChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.pill,
  },
  quickChipLabel: {
    color: colors.text,
    fontSize: 13,
    fontWeight: "600",
  },
  threadShell: {
    flex: 1,
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.lg,
    padding: spacing.md,
  },
  threadContent: {
    paddingBottom: spacing.lg,
  },
  composerShell: {
    marginTop: spacing.lg,
    flexDirection: "row",
    gap: spacing.md,
    alignItems: "center",
  },
  input: {
    flex: 1,
    minHeight: 54,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.lg,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.text,
    fontSize: 16,
  },
  sendButton: {
    minHeight: 54,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.pill,
    backgroundColor: colors.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  sendButtonDisabled: {
    opacity: 0.55,
  },
  sendLabel: {
    color: "#fffdf9",
    fontSize: 15,
    fontWeight: "700",
  },
});
