<template>
  <div
    v-if="isOpen"
    ref="panelRef"
    class="fixed w-96 max-h-96 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50 flex flex-col"
    :style="{ top: position.y + 'px', left: position.x + 'px' }"
  >
    <div
      class="flex items-center justify-between px-3 py-2 border-b border-gray-700 bg-gray-800 rounded-t-lg cursor-move select-none"
      @mousedown="startDrag"
    >
      <span class="text-sm font-semibold text-gray-300">Debug Traces</span>
      <div class="flex items-center gap-2">
        <span :class="connected ? 'text-green-400' : 'text-red-400'" class="text-xs">
          {{ connected ? 'Connected' : 'Disconnected' }}
        </span>
        <button @click="clearTraces" class="text-gray-400 hover:text-white text-xs px-2 py-1 rounded bg-gray-700">
          Clear
        </button>
        <button @click="$emit('close')" class="text-gray-400 hover:text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    <div ref="traceContainer" class="flex-1 overflow-y-auto p-2 space-y-1 text-xs font-mono">
      <div v-if="traces.length === 0" class="text-gray-500 italic">
        Waiting for traces...
      </div>
      <div
        v-for="(trace, index) in traces"
        :key="index"
        class="p-2 rounded bg-gray-800 border-l-2"
        :class="{
          'border-blue-500': trace.stage === 'request_start',
          'border-green-500': trace.stage === 'request_end',
          'border-yellow-500': trace.stage === 'detection',
          'border-purple-500': trace.stage === 'mcp_call',
          'border-red-500': trace.stage === 'error',
        }"
      >
        <div class="flex justify-between text-gray-400">
          <span class="font-semibold text-gray-200">{{ trace.stage }}</span>
          <span>{{ formatTime(trace.timestamp) }}</span>
        </div>
        <pre class="text-gray-300 mt-1 whitespace-pre-wrap break-all">{{ JSON.stringify(trace.data, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  isOpen: Boolean,
})

defineEmits(['close'])

const traces = ref([])
const connected = ref(false)
const traceContainer = ref(null)
const panelRef = ref(null)
const position = ref({ x: window.innerWidth - 420, y: window.innerHeight - 420 })
let ws = null
let isDragging = false
let dragOffset = { x: 0, y: 0 }

function startDrag(e) {
  isDragging = true
  dragOffset.x = e.clientX - position.value.x
  dragOffset.y = e.clientY - position.value.y
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(e) {
  if (!isDragging) return
  position.value.x = Math.max(0, Math.min(window.innerWidth - 400, e.clientX - dragOffset.x))
  position.value.y = Math.max(0, Math.min(window.innerHeight - 100, e.clientY - dragOffset.y))
}

function stopDrag() {
  isDragging = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

function formatTime(ts) {
  const d = new Date(ts * 1000)
  return d.toLocaleTimeString('en-US', { hour12: false }) + '.' + String(d.getMilliseconds()).padStart(3, '0')
}

function clearTraces() {
  traces.value = []
}

function connect() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = new WebSocket(`${protocol}//${window.location.host}/ws/debug`)

  ws.onopen = () => {
    connected.value = true
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      // data = { trace_id, traces: [{stage, timestamp, data}, ...] }
      if (data.traces) {
        for (const trace of data.traces) {
          traces.value.push(trace)
        }
      }
    } catch {
      // ignore malformed
    }
  }

  ws.onclose = () => {
    connected.value = false
    // Reconnect after delay
    setTimeout(connect, 3000)
  }

  ws.onerror = () => {
    connected.value = false
  }
}

watch(
  () => traces.value.length,
  async () => {
    await nextTick()
    if (traceContainer.value) {
      traceContainer.value.scrollTop = traceContainer.value.scrollHeight
    }
  }
)

onMounted(() => {
  if (props.isOpen) {
    connect()
  }
})

watch(
  () => props.isOpen,
  (open) => {
    if (open && !ws) {
      connect()
    }
  }
)

onUnmounted(() => {
  if (ws) {
    ws.onclose = null
    ws.close()
  }
})
</script>
