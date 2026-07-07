import React, { startTransition, useEffect, useState } from "react";
import {
  Alert,
  Linking,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { IntegrationCard } from "../components/IntegrationCard";
import { currentUserId } from "../config";
import {
  type ConnectedAccount,
  connectIntegration,
  listConnectedAccounts,
} from "../services/api";
import { colors, radius, spacing } from "../theme/tokens";


type ProviderConfig = {
  id: string;
  title: string;
  suite: string;
  app: string;
  description: string;
  detail: string;
  supported: boolean;
};

const PROVIDERS: ProviderConfig[] = [
  {
    id: "gmail",
    title: "Gmail",
    suite: "google",
    app: "gmail",
    description: "Mail send, read, and summary flows through your Composio Gmail auth config.",
    detail: "Use this first for email drafting, approvals, and inbox-powered assistant actions.",
    supported: true,
  },
  {
    id: "google-calendar",
    title: "Google Calendar",
    suite: "google",
    app: "googlecalendar",
    description: "Calendar read and scheduling actions through your Composio Google Calendar auth config.",
    detail: "Use this for meeting lookup, day plans, and event creation with approval gates.",
    supported: true,
  },
  {
    id: "microsoft-365",
    title: "Microsoft 365",
    suite: "microsoft",
    app: "office365",
    description: "Outlook, Teams, OneDrive, and calendar actions through Composio.",
    detail: "Use this for Outlook mail, Teams posting, OneDrive search, and M365 scheduling.",
    supported: true,
  },
  {
    id: "meta-ads",
    title: "Meta Ads",
    suite: "meta",
    app: "ads",
    description: "Planned next. Only the ads surface is in scope when Meta support ships.",
    detail: "General Meta messaging and social surfaces are not wired in this scaffold yet.",
    supported: false,
  },
];

function getStatusLabel(account: ConnectedAccount | undefined, supported: boolean) {
  if (!supported) {
    return "Planned";
  }

  if (!account) {
    return "Not Connected";
  }

  return account.status === "ready"
    ? "Connected"
    : account.status === "connecting"
      ? "Connecting"
      : account.status === "error"
        ? "Needs Attention"
        : account.status === "disconnected"
          ? "Disconnected"
          : account.status;
}

function getStatusTone(
  account: ConnectedAccount | undefined,
  supported: boolean,
): "ready" | "connecting" | "planned" {
  if (!supported) {
    return "planned";
  }

  return account?.status === "ready" ? "ready" : "connecting";
}

function getActionLabel(account: ConnectedAccount | undefined, supported: boolean) {
  if (!supported) {
    return "Coming Soon";
  }

  return account ? "Reconnect" : "Connect";
}

export function IntegrationsScreen() {
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [busyProviderId, setBusyProviderId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshAccounts = async () => {
    setError(null);
    setLoading(true);
    try {
      const result = await listConnectedAccounts();
      startTransition(() => {
        setAccounts(result);
      });
    } catch (refreshError) {
      setError(
        refreshError instanceof Error ? refreshError.message : "Could not load integration status.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refreshAccounts();
  }, []);

  const handleConnect = async (provider: ProviderConfig) => {
    if (!provider.supported) {
      Alert.alert("Not ready yet", "Meta Ads is documented but not wired in this scaffold yet.");
      return;
    }

    setBusyProviderId(provider.id);
    try {
      const result = await connectIntegration({
        user_id: currentUserId,
        suite: provider.suite,
        app: provider.app,
      });

      try {
        await Linking.openURL(result.connection_url);
      } catch {
        Alert.alert(
          "Connection link ready",
          "The connection link was created, but it could not be opened automatically on this device.",
        );
      }

      await refreshAccounts();
    } catch (connectError) {
      Alert.alert(
        "Connection failed",
        connectError instanceof Error ? connectError.message : "Could not start the connection flow.",
      );
    } finally {
      setBusyProviderId(null);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={() => void refreshAccounts()} />}
    >
      <View style={styles.hero}>
        <Text style={styles.title}>Integrations</Text>
        <Text style={styles.subtitle}>
          Connect the work accounts your voice assistant can use. Gmail and Google Calendar are
          ready for the first test pass. Microsoft stays available for the next phase, and Meta
          stays clearly marked until its exact scope is built.
        </Text>
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={styles.list}>
        {PROVIDERS.map((provider) => {
          const account = accounts.find(
            (item) =>
              item.suite === provider.suite &&
              item.app.trim().toLowerCase() === provider.app.trim().toLowerCase(),
          );

          return (
            <IntegrationCard
              key={provider.id}
              title={provider.title}
              description={provider.description}
              detail={
                account
                  ? `${provider.detail} Current status: ${account.status}.`
                  : provider.detail
              }
              statusLabel={getStatusLabel(account, provider.supported)}
              statusTone={getStatusTone(account, provider.supported)}
              actionLabel={busyProviderId === provider.id ? "Preparing..." : getActionLabel(account, provider.supported)}
              disabled={busyProviderId === provider.id}
              onPress={() => void handleConnect(provider)}
            />
          );
        })}
      </View>

      <View style={styles.footerCard}>
        <Text style={styles.footerTitle}>What happens after connect</Text>
        <Text style={styles.footerText}>
          The app stores the connected account reference, not raw Google or Microsoft provider
          tokens. Risky actions still pause for approval before they execute.
        </Text>
      </View>
    </ScrollView>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xxl,
  },
  hero: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  title: {
    color: colors.text,
    fontSize: 28,
    fontWeight: "700",
  },
  subtitle: {
    color: colors.textMuted,
    marginTop: spacing.sm,
    fontSize: 14,
    lineHeight: 21,
  },
  error: {
    color: colors.error,
    marginBottom: spacing.md,
  },
  list: {
    gap: spacing.md,
  },
  footerCard: {
    marginTop: spacing.lg,
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.lg,
    padding: spacing.lg,
  },
  footerTitle: {
    color: colors.text,
    fontWeight: "700",
    fontSize: 16,
  },
  footerText: {
    color: colors.textMuted,
    fontSize: 14,
    lineHeight: 20,
    marginTop: spacing.sm,
  },
});
