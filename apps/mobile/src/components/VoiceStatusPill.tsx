import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { VoiceState } from "../store/chatStore";
import { colors, radius, spacing } from "../theme/tokens";


const labels: Record<VoiceState, string> = {
  hold_ready: "Hold to Talk",
  idle_passive: "Wake Word Armed",
  wake_detected: "Wake Word Heard",
  capturing_command: "Listening",
  processing_turn: "Processing",
  executing_task: "Working",
  awaiting_approval: "Need Approval",
  speaking_result: "Speaking",
  followup_listening: "Listening Again",
  error_recovery: "Needs Attention",
};

const activeStates: VoiceState[] = [
  "idle_passive",
  "wake_detected",
  "capturing_command",
  "processing_turn",
  "executing_task",
  "awaiting_approval",
  "speaking_result",
  "followup_listening",
];

export function VoiceStatusPill({ state }: { state: VoiceState }) {
  const isActive = activeStates.includes(state);
  const isWarning = state === "awaiting_approval" || state === "error_recovery";

  return (
    <View
      style={[
        styles.pill,
        isActive ? styles.pillActive : null,
        isWarning ? styles.pillWarning : null,
      ]}
    >
      <View
        style={[
          styles.dot,
          isActive ? styles.dotActive : null,
          state === "error_recovery" ? styles.dotError : null,
        ]}
      />
      <Text style={styles.label}>{labels[state]}</Text>
    </View>
  );
}


const styles = StyleSheet.create({
  pill: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    backgroundColor: colors.surfaceMuted,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.pill,
    gap: spacing.sm,
  },
  pillActive: {
    backgroundColor: colors.accentSoft,
  },
  pillWarning: {
    backgroundColor: colors.warningSoft,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 8,
    backgroundColor: colors.textMuted,
  },
  dotActive: {
    backgroundColor: colors.accent,
  },
  dotError: {
    backgroundColor: colors.error,
  },
  label: {
    color: colors.text,
    fontSize: 13,
    fontWeight: "600",
  },
});
