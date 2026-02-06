<template>
  <div class="h-full w-full relative">
    <iframe
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
import { ref } from 'vue'

const port = import.meta.env.VITE_OPENWEBUI_PORT || '8082'
const openWebuiUrl = `${window.location.protocol}//${window.location.hostname}:${port}`

const overlayRef = ref(null)
defineExpose({ overlayRef })
</script>
