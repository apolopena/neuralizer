<template>
  <div class="flex h-screen">
    <!-- Left pane: Intercepted prompts -->
    <div class="w-1/2 border-r border-gray-800">
      <SanitizedPanel />
    </div>
    <!-- Right pane: Open WebUI chat -->
    <div class="w-1/2">
      <ChatPanel />
    </div>
  </div>
</template>

<script setup>
import SanitizedPanel from "../components/SanitizedPanel.vue";
import ChatPanel from "../components/ChatPanel.vue";
</script>
