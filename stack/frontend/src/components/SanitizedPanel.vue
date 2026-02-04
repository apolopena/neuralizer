<template>
  <div class="flex flex-col h-full bg-gray-950 text-gray-100">
    <div class="px-4 py-3 border-b border-gray-800">
      <h2 class="text-sm font-semibold uppercase tracking-wide text-gray-400">
        Intercepted Prompts
      </h2>
    </div>
    <div ref="scrollContainer" class="flex-1 overflow-y-auto p-4 space-y-3">
      <div v-if="prompts.length === 0" class="text-gray-500 text-sm italic">
        Waiting for prompts...
      </div>
      <div
        v-for="(entry, index) in prompts"
        :key="index"
        class="rounded-lg bg-gray-900 border border-gray-800 p-3"
      >
        <p class="text-sm text-gray-400 whitespace-pre-wrap">{{ entry.prompt }}</p>
        <p v-if="entry.sanitized" class="mt-2 text-sm text-gray-200 whitespace-pre-wrap">{{ entry.sanitized }}</p>
        <p
          class="mt-1 text-xs"
          :class="{
            'text-yellow-500 animate-pulse': entry.status === 'Processing...',
            'text-red-500': entry.status === 'Error',
            'text-green-500': entry.status !== 'Processing...' && entry.status !== 'Error',
          }"
        >{{ entry.status }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";

const prompts = ref([]);
const scrollContainer = ref(null);
let ws = null;

function connect() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${protocol}//${window.location.host}/ws/prompts`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      // Update existing entry if same prompt is being processed
      const existing = prompts.value.findLastIndex(
        (p) => p.prompt === data.prompt && p.status === "Processing..."
      );
      if (existing !== -1 && data.status !== "Processing...") {
        prompts.value[existing] = data;
      } else {
        prompts.value.push(data);
      }
    } catch {
      // ignore malformed messages
    }
  };

  ws.onclose = () => {
    // Reconnect after a brief delay
    setTimeout(connect, 2000);
  };
}

watch(
  () => prompts.value.length,
  async () => {
    await nextTick();
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  }
);

onMounted(() => {
  connect();
});

onUnmounted(() => {
  if (ws) {
    ws.onclose = null; // prevent reconnect
    ws.close();
  }
});
</script>
