<template>
  <router-view />
  <GameEffectOverlay />
  <Toast />
</template>

<script setup lang="ts">
import GameEffectOverlay from '@/components/game/GameEffectOverlay.vue'
import Toast from '@/components/game/Toast.vue'
</script>
