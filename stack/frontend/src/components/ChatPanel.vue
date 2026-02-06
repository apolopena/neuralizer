<template>
  <div class="h-full w-full">
    <iframe
      :src="openWebuiUrl"
      class="h-full w-full border-0"
      title="Open WebUI Chat"
    />
  </div>
</template>

<script setup>
const port = import.meta.env.VITE_OPENWEBUI_PORT || '8082'
const openWebuiUrl = `${window.location.protocol}//${window.location.hostname}:${port}`
</script>
