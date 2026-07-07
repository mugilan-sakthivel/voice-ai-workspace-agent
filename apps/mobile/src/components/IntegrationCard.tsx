import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "../theme/tokens";


type Props = {
  title: string;
  description: string;
  statusLabel: string;
  statusTone: "ready" | "connecting" | "planned";
  actionLabel: string;
  disabled?: boolean;
  detail?: string;
  onPress: () => void;
};

export function IntegrationCard({
  title,
  description,
  statusLabel,
  statusTone,
  actionLabel,
  disabled,
  detail,
  onPress,
}: Props) {
  const statusToneStyle =
    statusTone === "ready"
      ? styles.statusReady
      : statusTone === "connecting"
        ? styles.statusConnecting
        : styles.statusPlanned;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.copy}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.description}>{description}</Text>
        </View>
        <View style={[styles.statusPill, statusToneStyle]}>
          <Text style={styles.statusLabel}>{statusLabel}</Text>
        </View>
      </View>

      {detail ? <Text style={styles.detail}>{detail}</Text> : null}

      <Pressable
        disabled={disabled}
        style={[styles.button, disabled ? styles.buttonDisabled : null]}
        onPress={onPress}
      >
        <Text style={[styles.buttonLabel, disabled ? styles.buttonLabelDisabled : null]}>
          {actionLabel}
        </Text>
      </Pressable>
    </View>
  );
}


const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  copy: {
    flex: 1,
    gap: spacing.xs,
  },
  title: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "700",
  },
  description: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 20,
  },
  statusPill: {
    alignSelf: "flex-start",
    borderRadius: radius.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  statusReady: {
    backgroundColor: colors.successSoft,
  },
  statusConnecting: {
    backgroundColor: colors.accentSoft,
  },
  statusPlanned: {
    backgroundColor: colors.surfaceMuted,
  },
  statusLabel: {
    color: colors.text,
    fontWeight: "600",
    fontSize: 12,
  },
  detail: {
    color: colors.textMuted,
    marginTop: spacing.md,
    fontSize: 13,
    lineHeight: 18,
  },
  button: {
    marginTop: spacing.lg,
    minHeight: 48,
    borderRadius: radius.pill,
    backgroundColor: colors.accent,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonDisabled: {
    backgroundColor: colors.surfaceMuted,
  },
  buttonLabel: {
    color: "#fffdf9",
    fontWeight: "700",
    fontSize: 15,
  },
  buttonLabelDisabled: {
    color: colors.textMuted,
  },
});
