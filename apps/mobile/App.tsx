import { StatusBar } from "expo-status-bar";
import React, { useState } from "react";
import { StyleSheet, View } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

import { ScreenTabs } from "./src/components/ScreenTabs";
import { ChatScreen } from "./src/screens/ChatScreen";
import { IntegrationsScreen } from "./src/screens/IntegrationsScreen";
import { colors } from "./src/theme/tokens";


export default function App() {
  const [screen, setScreen] = useState<"assistant" | "integrations">("assistant");

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container} edges={["top", "left", "right"]}>
        <StatusBar style="dark" />
        <ScreenTabs active={screen} onChange={setScreen} />
        <View style={styles.content}>
          {screen === "assistant" ? <ChatScreen /> : <IntegrationsScreen />}
        </View>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
  },
});
