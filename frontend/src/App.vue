<!-- /src/App.vue -->
<script setup lang="ts">
  import Drawer from '@/components/Drawer.vue'
  import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
  <Drawer />
</template>

<style>
  html,
  body,
  #app {
    width: 100%;
    min-width: 0;
    max-width: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
  }

  body.no-scroll {
    overflow: hidden !important;
    position: fixed;
    width: 100%;
  }
</style>
