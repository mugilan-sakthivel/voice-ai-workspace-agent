import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { VoiceState } from "../store/chatStore";
import { colors, radius, spacing } from "../theme/tokens";


export function HoldToTalkButton({
  disabled,
  state,
  onPressIn,
  onPressOut,
}: {
  disabled?: boolean;
  state: VoiceState;
  onPressIn: () => void;
  onPressOut: () => void;
}) {
  const active = state === "capturing_command";

  return (
    <Pressable
      disabled={disabled}
      style={[
        styles.button,
        active ? styles.buttonActive : null,
        disabled ? styles.buttonDisabled : null,
      ]}
      onPressIn={onPressIn}
      onPressOut={onPressOut}
    >
      <View
        style={[
          styles.core,
          active ? styles.coreActive : null,
          disabled ? styles.coreDisabled : null,
        ]}
      />
      <Text style={styles.label}>{active ? "Release to send" : "Hold to talk"}</Text>
      <Text style={styles.caption}>Use this as a fallback when wake-word listening is off.</Text>
    </Pressable>
  );
}


const styles = StyleSheet.create({
  button: {
    marginTop: spacing.lg,
    borderRadius: radius.lg,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.lg,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonActive: {
    backgroundColor: colors.accentSoft,
    borderColor: colors.accent,
  },
  buttonDisabled: {
    opacity: 0.55,
  },
  core: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.accent,
    marginBottom: spacing.sm,
  },
  coreActive: {
    backgroundColor: colors.error,
  },
  coreDisabled: {
    backgroundColor: colors.textMuted,
  },
  label: {
    color: colors.text,
    fontWeight: "600",
    fontSize: 15,
  },
  caption: {
    color: colors.textMuted,
    fontSize: 12,
    marginTop: spacing.xs,
  },
});
