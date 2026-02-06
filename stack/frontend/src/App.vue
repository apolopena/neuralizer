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
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import SettingsDrawer from './components/SettingsDrawer.vue'

const isScrubbing = ref(true)
const settingsOpen = ref(false)

function handleModeChange(scrubbing) {
  isScrubbing.value = scrubbing
}
</script>
