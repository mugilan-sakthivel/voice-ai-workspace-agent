import Constants from "expo-constants";


type RuntimeEnv = {
  process?: {
    env?: Record<string, string | undefined>;
  };
};

const env = (globalThis as typeof globalThis & RuntimeEnv).process?.env ?? {};
const extra = Constants.expoConfig?.extra ?? {};

export const currentUserId = "demo-user";
export const apiUrl =
  env.EXPO_PUBLIC_API_URL ??
  (typeof extra.apiUrl === "string" ? extra.apiUrl : "http://localhost:8000");
export const wsUrl =
  env.EXPO_PUBLIC_WS_URL ??
  (typeof extra.wsUrl === "string" ? extra.wsUrl : "ws://localhost:8000");
