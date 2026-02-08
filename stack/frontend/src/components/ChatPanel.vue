<template>
  <div class="h-full w-full relative bg-gray-950">
    <!-- Loading state while Open WebUI starts -->
    <div v-if="!isReady" class="absolute inset-0 flex flex-col items-center justify-center">
      <!-- Circles-in-a-circle loader -->
      <div class="loader mb-4">
        <div v-for="i in 8" :key="i" class="dot" :style="{ '--i': i }" />
      </div>
      <span class="text-sm text-cyan-400">{{ statusMessage }}</span>
    </div>
    <!-- Iframe shown once ready -->
    <iframe
      v-if="isReady"
      :src="openWebuiUrl"
      class="h-full w-full border-0"
      title="Open WebUI Chat"
    />
    <!-- Overlay for animation protection — prevents iframe reflow jank during pane resize -->
    <div ref="overlayRef"
         class="absolute inset-0 bg-gray-950 pointer-events-none hidden" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  isScrubbing: Boolean,
})

const port = import.meta.env.VITE_OPENWEBUI_PORT || '8082'
const baseUrl = `${window.location.protocol}//${window.location.hostname}:${port}`
const cacheBuster = ref(Date.now())
const chatPath = ref('')
const openWebuiUrl = computed(() => `${baseUrl}${chatPath.value}?_t=${cacheBuster.value}`)

const isReady = ref(false)
const statusMessage = ref('Starting up')
const overlayRef = ref(null)
let pollInterval = null

// Fetch latest chat ID from OWU API
async function getLatestChatId() {
  try {
    const resp = await fetch(`${baseUrl}/api/v1/chats/list`, { credentials: 'include' })
    if (resp.ok) {
      const data = await resp.json()
      if (data && data.length > 0) {
        return data[0].id
      }
    }
  } catch {
    // Ignore errors, just return null
  }
  return null
}

// Reload iframe when scrubbing mode changes
// TODO: Re-enable chat restoration when sync issues are resolved
watch(() => props.isScrubbing, async () => {
  // const chatId = await getLatestChatId()
  // chatPath.value = chatId ? `/c/${chatId}` : ''
  cacheBuster.value = Date.now()
})

async function checkHealth() {
  try {
    const resp = await fetch('/api/health/openwebui')
    if (resp.ok) {
      const data = await resp.json()
      statusMessage.value = data.message
      if (data.status === 'ready') {
        isReady.value = true
        if (pollInterval) {
          clearInterval(pollInterval)
          pollInterval = null
        }
      }
    }
  } catch {
    statusMessage.value = 'Waiting for backend'
  }
}

onMounted(() => {
  checkHealth()
  pollInterval = setInterval(checkHealth, 1000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})

defineExpose({ overlayRef })
</script>

<style scoped>
.loader {
  position: relative;
  width: 48px;
  height: 48px;
}

.dot {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #22d3ee; /* cyan-400 */
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: rotate(calc(45deg * var(--i))) translateY(-18px);
  transform-origin: center center;
  animation: pulse 1s ease-in-out infinite;
  animation-delay: calc(0.125s * var(--i));
  opacity: 0.2;
}

@keyframes pulse {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}
</style>
