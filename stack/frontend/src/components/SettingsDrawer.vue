<template>
  <!-- Backdrop -->
  <div ref="backdropRef" class="fixed inset-0 bg-black/50 z-40"
       :class="{ hidden: !visible }" @click="close" />

  <!-- Drawer -->
  <aside ref="drawerRef" role="dialog" aria-modal="true"
         aria-label="Settings"
         class="fixed top-0 left-0 h-full w-80 bg-gray-900 border-r border-gray-700 z-50 shadow-xl"
         :class="{ hidden: !visible }">
    <div class="flex items-center justify-between p-4 border-b border-gray-800">
      <h2 class="text-lg font-semibold text-gray-100">Settings</h2>
      <button @click="close" class="text-gray-400 hover:text-gray-200" aria-label="Close settings">&#10005;</button>
    </div>

    <div class="p-4 space-y-6">
      <!-- Scrubbing Settings -->
      <div>
        <h3 class="text-sm font-semibold text-gray-300 uppercase tracking-wide mb-3">Scrubbing Settings</h3>
        <div class="space-y-3">
          <label class="block">
            <span class="text-sm text-gray-400">Replacement Strategy</span>
            <select disabled class="mt-1 w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-500 cursor-not-allowed">
              <option>[REDACTED]</option>
              <option>████</option>
              <option>Fake substitution</option>
            </select>
            <span class="text-xs text-gray-600 mt-1 block">Coming soon</span>
          </label>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useGsap } from '../composables/useGsap.js'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])

const { gsap, slideTo } = useGsap()
const drawerRef = ref(null)
const backdropRef = ref(null)
const visible = ref(false)
let ctx
let activeTl = null

onMounted(() => {
  ctx = gsap.context(() => {}, drawerRef.value)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  ctx?.revert()
  document.removeEventListener('keydown', handleKeydown)
})

watch(() => props.open, async (isOpen) => {
  if (activeTl) { activeTl.kill(); activeTl = null }

  if (isOpen) {
    visible.value = true
    await nextTick()
    ctx.add(() => { activeTl = slideTo(drawerRef.value, backdropRef.value, true, { fromLeft: true }) })
  } else if (visible.value) {
    ctx.add(() => {
      activeTl = slideTo(drawerRef.value, backdropRef.value, false, { fromLeft: true })
      activeTl.then(() => { visible.value = false; activeTl = null })
    })
  }
})

function close() {
  emit('close')
}

function handleKeydown(e) {
  if (e.key === 'Escape' && props.open) close()
}
</script>
