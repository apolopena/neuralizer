<template>
  <div id="app" class="h-screen flex flex-col bg-[var(--color-bg-app)]">
    <AppHeader
      :is-scrubbing="isScrubbing"
      @mode-change="handleModeChange"
      @toggle-settings="settingsOpen = !settingsOpen"
    />
    <router-view v-slot="{ Component }">
      <component :is="Component" :is-scrubbing="isScrubbing" />
    </router-view>
    <SettingsDrawer :open="settingsOpen" @close="settingsOpen = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import SettingsDrawer from './components/SettingsDrawer.vue'

const isScrubbing = ref(true)
const settingsOpen = ref(false)

onMounted(async () => {
  try {
    await fetch('/v1/mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scrubbing: true }),
    })
  } catch {
    // Backend unreachable — local state already defaults to scrubbing on
  }
})

async function handleModeChange(scrubbing) {
  try {
    const resp = await fetch('/v1/mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scrubbing }),
    })
    if (!resp.ok) return
    isScrubbing.value = scrubbing
  } catch {
    // Network error — don't change local state
  }
}
</script>
