<template>
  <header class="h-20 bg-black flex items-center px-4 gap-3 shrink-0">
    <!-- Logo -->
    <div class="relative shrink-0">
      <img src="../assets/logo-header.png" alt="NeurALIzer" class="h-14" />
      <!-- Disabled indicator — always rendered, animated via GSAP stroke-dashoffset -->
      <svg ref="disabledSvgRef" class="absolute -inset-2 w-[calc(100%+16px)] h-[calc(100%+16px)]"
           viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" style="display: none">
        <!-- Red border (underneath) -->
        <circle class="dis-circle" cx="50" cy="50" r="40" fill="none" stroke="rgba(239, 68, 68, 0.3)" stroke-width="10" />
        <line class="dis-line" x1="22" y1="22" x2="78" y2="78" stroke="rgba(239, 68, 68, 0.3)" stroke-width="10" stroke-linecap="round" />
        <!-- Cyan fill (on top) -->
        <circle class="dis-circle" cx="50" cy="50" r="40" fill="none" stroke="rgba(165, 243, 252, 0.5)" stroke-width="4" />
        <line class="dis-line" x1="22" y1="22" x2="78" y2="78" stroke="rgba(165, 243, 252, 0.5)" stroke-width="4" stroke-linecap="round" />
      </svg>
    </div>

    <!-- Status Pill -->
    <div ref="pillRef" role="switch" tabindex="0" :aria-checked="isScrubbing"
         :aria-label="isScrubbing ? 'Scrubbing active' : 'Direct mode'"
         class="rounded-full px-3 py-1.5 flex items-center gap-2 text-sm cursor-pointer
                bg-gray-900 border border-gray-700 hover:border-gray-500 text-gray-300"
         @click="handlePillClick"
         @keydown.enter="handlePillClick"
         @keydown.space.prevent="handlePillClick">
      <!-- Default state -->
      <template v-if="!confirming">
        <span class="w-2 h-2 rounded-full" :class="dotClass"></span>
        <span>{{ pillText }}</span>
      </template>
      <!-- Confirmation state -->
      <template v-else>
        <span>Stop intercepting? This will start a free chat session.</span>
        <button @click.stop="cancelConfirm"
                class="w-6 h-6 rounded-full bg-red-950 hover:bg-red-900 text-red-600 text-xs flex items-center justify-center"
                aria-label="Cancel">&#10005;</button>
        <button @click.stop="confirmDisable"
                class="w-6 h-6 rounded-full bg-green-950 hover:bg-green-900 text-green-600 text-xs flex items-center justify-center"
                aria-label="Confirm">&#10003;</button>
      </template>
    </div>

    <!-- Settings Gear -->
    <button @click="$emit('toggle-settings')" class="text-gray-400 hover:text-gray-200"
            aria-label="Settings">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
      </svg>
    </button>
  </header>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useGsap } from '../composables/useGsap.js'

const props = defineProps({ isScrubbing: Boolean })
const emit = defineEmits(['mode-change', 'toggle-settings'])

const { gsap, defaults } = useGsap()
const pillRef = ref(null)
const disabledSvgRef = ref(null)
const confirming = ref(false)

// Stroke lengths for draw animation
const CIRCLE_LEN = 2 * Math.PI * 40  // ~251
const LINE_LEN = Math.sqrt(56 * 56 + 56 * 56)  // ~79

const dotClass = computed(() =>
  props.isScrubbing
    ? 'bg-[var(--color-scrub-active)] animate-pulse'
    : 'bg-[var(--color-scrub-inactive)]'
)

const pillText = computed(() =>
  props.isScrubbing
    ? 'Prompts are being intercepted and scrubbed'
    : 'Free chat — prompts are not intercepted'
)

// Animate the disabled indicator SVG in/out
watch(() => props.isScrubbing, (scrubbing) => {
  const svg = disabledSvgRef.value
  if (!svg) return

  const circles = svg.querySelectorAll('.dis-circle')
  const lines = svg.querySelectorAll('.dis-line')

  if (!scrubbing) {
    // Draw in: show SVG, circle draws first, then slash
    gsap.set(svg, { display: 'block' })
    gsap.set(circles, { strokeDasharray: CIRCLE_LEN, strokeDashoffset: CIRCLE_LEN })
    gsap.set(lines, { strokeDasharray: LINE_LEN, strokeDashoffset: LINE_LEN })
    gsap.to(circles, { strokeDashoffset: 0, duration: 0.4, ease: 'power2.out' })
    gsap.to(lines, { strokeDashoffset: 0, duration: 0.3, ease: 'power2.out', delay: 0.2 })
  } else {
    // Draw out: slash erases first, then circle
    gsap.to(lines, { strokeDashoffset: LINE_LEN, duration: 0.2, ease: 'power2.in' })
    gsap.to(circles, {
      strokeDashoffset: CIRCLE_LEN,
      duration: 0.3,
      ease: 'power2.in',
      delay: 0.1,
      onComplete: () => gsap.set(svg, { display: 'none' })
    })
  }
})

async function animatePillMorph() {
  const el = pillRef.value
  if (!el) return
  const oldWidth = el.offsetWidth
  // Lock width and prevent text reflow before content swap
  gsap.set(el, { width: oldWidth, overflow: 'hidden', whiteSpace: 'nowrap' })
  confirming.value = !confirming.value
  await nextTick()
  const newWidth = el.scrollWidth
  gsap.to(el, {
    width: newWidth,
    duration: defaults.durationPill,
    ease: defaults.easePill,
    onComplete: () => gsap.set(el, { clearProps: 'width,overflow,whiteSpace' })
  })
}

function handlePillClick() {
  if (confirming.value) return
  if (props.isScrubbing) {
    animatePillMorph()
  } else {
    emit('mode-change', true)
  }
}

function confirmDisable() {
  animatePillMorph()
  emit('mode-change', false)
}

function cancelConfirm() {
  animatePillMorph()
}
</script>
