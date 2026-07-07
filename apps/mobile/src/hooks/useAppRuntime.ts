import { useLocalRuntime } from "@assistant-ui/react-native";

import { chatAdapter } from "../adapters/chatAdapter";


export function useAppRuntime() {
  return useLocalRuntime(chatAdapter);
}

