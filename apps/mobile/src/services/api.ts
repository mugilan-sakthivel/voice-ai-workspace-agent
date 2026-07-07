import { apiUrl, currentUserId } from "../config";


export type ChatPayload = {
  thread_id: string;
  user_id: string;
  message: string;
  input_mode: "text" | "voice";
};

export type ChatResult = {
  thread_id: string;
  message_id: string;
  reply: string;
  status: "completed" | "approval_required";
  approval?: {
    approval_id: string;
    action_summary: string;
    tool_name: string;
  } | null;
};

export type ApprovalResult = {
  approval_id: string;
  status: "approved" | "rejected";
  message: string;
};

export type IntegrationConnectPayload = {
  user_id: string;
  suite: string;
  app: string;
};

export type IntegrationConnectResult = {
  connection_url: string;
  integration_id: string;
  expires_at: string;
};

export type ConnectedAccount = {
  suite: string;
  app: string;
  status: string;
  connected_account_id: string;
};

export type TranscriptionResult = {
  text: string;
  provider: string;
  model: string;
  is_final: boolean;
};


async function buildRequestError(response: Response, fallbackMessage: string): Promise<Error> {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string" && payload.detail) {
      return new Error(payload.detail);
    }
  } catch {
    // Ignore parsing errors and fall back to the generic message.
  }

  return new Error(fallbackMessage);
}


export async function sendChatMessage(payload: ChatPayload): Promise<ChatResult> {
  const response = await fetch(`${apiUrl}/api/v1/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw await buildRequestError(response, "Unable to reach the backend.");
  }

  return response.json();
}


export async function confirmApproval(approvalId: string): Promise<ApprovalResult> {
  const response = await fetch(`${apiUrl}/api/v1/approvals/${approvalId}/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: currentUserId }),
  });
  if (!response.ok) {
    throw await buildRequestError(response, "Approval confirmation failed.");
  }
  return response.json();
}


export async function rejectApproval(approvalId: string): Promise<ApprovalResult> {
  const response = await fetch(`${apiUrl}/api/v1/approvals/${approvalId}/reject`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: currentUserId }),
  });
  if (!response.ok) {
    throw await buildRequestError(response, "Approval rejection failed.");
  }
  return response.json();
}


export async function connectIntegration(
  payload: IntegrationConnectPayload,
): Promise<IntegrationConnectResult> {
  const response = await fetch(`${apiUrl}/api/v1/integrations/composio/connect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw await buildRequestError(response, "Unable to create the integration link.");
  }

  return response.json();
}


export async function listConnectedAccounts(): Promise<ConnectedAccount[]> {
  const response = await fetch(
    `${apiUrl}/api/v1/integrations/accounts?user_id=${encodeURIComponent(currentUserId)}`,
  );

  if (!response.ok) {
    throw await buildRequestError(response, "Unable to load integrations.");
  }

  return response.json();
}


export async function transcribeAudio(fileUri: string): Promise<TranscriptionResult> {
  const formData = new FormData();
  formData.append("file", {
    uri: fileUri,
    name: "voice-command.m4a",
    type: "audio/m4a",
  } as unknown as Blob);

  const response = await fetch(`${apiUrl}/api/v1/voice/stt`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw await buildRequestError(response, "Voice transcription failed.");
  }

  return response.json();
}
