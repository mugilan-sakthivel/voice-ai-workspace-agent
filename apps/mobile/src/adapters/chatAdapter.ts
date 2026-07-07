import type { ChatModelAdapter } from "@assistant-ui/react-native";

import { apiUrl, currentUserId } from "../config";
import { useChatStore } from "../store/chatStore";


export const chatAdapter: ChatModelAdapter = {
  async *run({ messages, abortSignal }) {
    const latest = messages[messages.length - 1];
    const { threadId } = useChatStore.getState();
    const textParts = latest?.content
      ?.reduce((acc, part) => {
        if (part.type === "text") {
          return `${acc}${acc ? "\n" : ""}${part.text}`;
        }
        return acc;
      }, "")
      .trim();

    const response = await fetch(`${apiUrl}/api/v1/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        thread_id: threadId,
        user_id: currentUserId,
        message: textParts || "Hello",
        input_mode: "text",
      }),
      signal: abortSignal,
    });

    if (!response.ok) {
      throw new Error("Unable to stream chat response.");
    }

    const data = await response.json();
    yield {
      content: [{ type: "text", text: data.reply }],
    };
  },
};
