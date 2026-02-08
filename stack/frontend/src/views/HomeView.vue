<template>
  <div ref="containerRef" class="flex flex-1 min-h-0">
    <!-- Left pane: Intercepted prompts -->
    <div ref="scrubPaneRef" class="border-r border-gray-800 min-w-0 overflow-hidden" style="flex-basis: 50%">
      <SanitizedPanel />
    </div>
    <!-- Right pane: Open WebUI chat -->
    <div ref="chatPaneRef" class="min-w-0" style="flex-basis: 50%; flex-grow: 1">
      <ChatPanel ref="chatPanelRef" :isScrubbing="isScrubbing" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { gsap } from 'gsap'
import SanitizedPanel from '../components/SanitizedPanel.vue'
import ChatPanel from '../components/ChatPanel.vue'

const props = defineProps({ isScrubbing: Boolean })

const containerRef = ref(null)
const scrubPaneRef = ref(null)
const chatPaneRef = ref(null)
const chatPanelRef = ref(null)

let activeTl = null

onUnmounted(() => {
  if (activeTl) { activeTl.kill(); activeTl = null }
})

watch(() => props.isScrubbing, (scrubbing) => {
  const scrub = scrubPaneRef.value
  const chat = chatPaneRef.value
  if (!scrub || !chat) return

  if (activeTl) { activeTl.kill(); activeTl = null }

  // Lock to pixel widths so GSAP animates actual size, not flex negotiation
  const scrubW = scrub.offsetWidth
  const chatW = chat.offsetWidth
  const totalW = scrubW + chatW

  gsap.set(scrub, { width: scrubW, flexBasis: 'auto', flexGrow: 0, flexShrink: 0 })
  gsap.set(chat, { width: chatW, flexBasis: 'auto', flexGrow: 0, flexShrink: 0 })

  const tl = gsap.timeline({
    onComplete() {
      // Restore flex layout at final state
      if (!scrubbing) {
        gsap.set(scrub, { clearProps: 'all' })
        gsap.set(chat, { clearProps: 'all' })
        scrub.style.flexBasis = '0%'
        chat.style.flexBasis = '100%'
        chat.style.flexGrow = '1'
      } else {
        gsap.set(scrub, { clearProps: 'all' })
        gsap.set(chat, { clearProps: 'all' })
        scrub.style.flexBasis = '50%'
        chat.style.flexBasis = '50%'
        chat.style.flexGrow = '1'
      }
      activeTl = null
    }
  })

  if (!scrubbing) {
    tl.to(scrub, { width: 0, duration: 0.6, ease: 'power2.out' }, 0)
      .to(chat, { width: totalW, duration: 0.6, ease: 'power2.out' }, 0)
  } else {
    tl.to(scrub, { width: totalW / 2, duration: 0.6, ease: 'power2.out' }, 0)
      .to(chat, { width: totalW / 2, duration: 0.6, ease: 'power2.out' }, 0)
  }

  activeTl = tl
})
</script>
