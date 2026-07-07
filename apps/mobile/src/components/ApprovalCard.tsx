import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "../theme/tokens";


type Props = {
  title: string;
  toolName: string;
  onApprove: () => void;
  onReject: () => void;
};


export function ApprovalCard({ title, toolName, onApprove, onReject }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.kicker}>Approval Required</Text>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.caption}>{toolName}</Text>
      <View style={styles.actions}>
        <Pressable style={[styles.button, styles.buttonGhost]} onPress={onReject}>
          <Text style={styles.buttonGhostLabel}>Cancel</Text>
        </Pressable>
        <Pressable style={[styles.button, styles.buttonPrimary]} onPress={onApprove}>
          <Text style={styles.buttonPrimaryLabel}>Approve</Text>
        </Pressable>
      </View>
    </View>
  );
}


const styles = StyleSheet.create({
  card: {
    marginTop: spacing.md,
    borderRadius: radius.lg,
    padding: spacing.lg,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  kicker: {
    color: colors.accent,
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase",
    marginBottom: spacing.sm,
  },
  title: {
    color: colors.text,
    fontSize: 16,
    lineHeight: 22,
    fontWeight: "600",
  },
  caption: {
    color: colors.textMuted,
    marginTop: spacing.sm,
  },
  actions: {
    flexDirection: "row",
    gap: spacing.md,
    marginTop: spacing.lg,
  },
  button: {
    flex: 1,
    minHeight: 48,
    borderRadius: radius.pill,
    alignItems: "center",
    justifyContent: "center",
  },
  buttonGhost: {
    backgroundColor: colors.surfaceMuted,
  },
  buttonPrimary: {
    backgroundColor: colors.accent,
  },
  buttonGhostLabel: {
    color: colors.text,
    fontWeight: "600",
  },
  buttonPrimaryLabel: {
    color: "#fffdf9",
    fontWeight: "700",
  },
});

