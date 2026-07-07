import React from "react";
import { StyleSheet, Text, View } from "react-native";

import { AppMessage } from "../store/chatStore";
import { colors, radius, spacing } from "../theme/tokens";


export function MessageBubble({ message }: { message: AppMessage }) {
  const isUser = message.role === "user";

  return (
    <View style={[styles.row, isUser ? styles.rowUser : null]}>
      <View style={[styles.bubble, isUser ? styles.bubbleUser : styles.bubbleAssistant]}>
        <Text style={[styles.text, isUser ? styles.textUser : null]}>{message.text}</Text>
      </View>
    </View>
  );
}


const styles = StyleSheet.create({
  row: {
    marginBottom: spacing.md,
    flexDirection: "row",
  },
  rowUser: {
    justifyContent: "flex-end",
  },
  bubble: {
    maxWidth: "86%",
    borderRadius: radius.lg,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  bubbleAssistant: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  bubbleUser: {
    backgroundColor: colors.accent,
  },
  text: {
    fontSize: 16,
    lineHeight: 22,
    color: colors.text,
  },
  textUser: {
    color: "#fffdf9",
  },
});

