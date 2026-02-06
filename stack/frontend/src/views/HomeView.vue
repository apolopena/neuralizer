<template>
  <div ref="containerRef" class="flex flex-1 min-h-0">
    <!-- Left pane: Intercepted prompts -->
    <div ref="scrubPaneRef" class="border-r border-gray-800" style="flex-basis: 50%">
      <SanitizedPanel />
    </div>
    <!-- Right pane: Open WebUI chat -->
    <div ref="chatPaneRef" style="flex-basis: 50%; flex-grow: 1">
      <ChatPanel ref="chatPanelRef" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import SanitizedPanel from '../components/SanitizedPanel.vue'
import ChatPanel from '../components/ChatPanel.vue'
import { useGsap } from '../composables/useGsap.js'

const props = defineProps({ isScrubbing: Boolean })

const { gsap, resizeTo } = useGsap()
const containerRef = ref(null)
const scrubPaneRef = ref(null)
const chatPaneRef = ref(null)
const chatPanelRef = ref(null)

let ctx
onMounted(() => {
  ctx = gsap.context(() => {}, containerRef.value)
})
onUnmounted(() => ctx?.revert())

watch(() => props.isScrubbing, (scrubbing) => {
  if (!scrubPaneRef.value || !chatPaneRef.value) return

  const overlayEl = chatPanelRef.value?.overlayRef

  ctx.add(() => {
    if (!scrubbing) {
      resizeTo(
        [
          { el: scrubPaneRef.value, to: '0%' },
          { el: chatPaneRef.value, to: '100%' },
        ],
        { fadeEl: scrubPaneRef.value, fadeOut: true, overlayEl }
      )
    } else {
      resizeTo(
        [
          { el: scrubPaneRef.value, to: '50%' },
          { el: chatPaneRef.value, to: '50%' },
        ],
        { fadeEl: scrubPaneRef.value, fadeOut: false, overlayEl }
      )
    }
  })
})
</script>
