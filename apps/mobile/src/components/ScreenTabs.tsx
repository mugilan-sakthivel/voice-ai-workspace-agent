import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "../theme/tokens";


type Props = {
  active: "assistant" | "integrations";
  onChange: (screen: "assistant" | "integrations") => void;
};

export function ScreenTabs({ active, onChange }: Props) {
  return (
    <View style={styles.shell}>
      <Pressable
        style={[styles.tab, active === "assistant" ? styles.tabActive : null]}
        onPress={() => onChange("assistant")}
      >
        <Text style={[styles.label, active === "assistant" ? styles.labelActive : null]}>
          Assistant
        </Text>
      </Pressable>
      <Pressable
        style={[styles.tab, active === "integrations" ? styles.tabActive : null]}
        onPress={() => onChange("integrations")}
      >
        <Text style={[styles.label, active === "integrations" ? styles.labelActive : null]}>
          Integrations
        </Text>
      </Pressable>
    </View>
  );
}


const styles = StyleSheet.create({
  shell: {
    flexDirection: "row",
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.pill,
    padding: spacing.xs,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.md,
  },
  tab: {
    flex: 1,
    minHeight: 42,
    borderRadius: radius.pill,
    alignItems: "center",
    justifyContent: "center",
  },
  tabActive: {
    backgroundColor: colors.surface,
  },
  label: {
    color: colors.textMuted,
    fontWeight: "600",
    fontSize: 14,
  },
  labelActive: {
    color: colors.text,
  },
});
