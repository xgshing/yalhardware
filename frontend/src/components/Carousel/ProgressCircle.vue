<!-- src/components/Carousel/ProgressCircle.vue -->
<template>
  <svg
    class="ring"
    viewBox="0 0 100 100"
  >
    <circle
      cx="50"
      cy="50"
      r="47"
      class="background-ring"
    />
    <circle
      cx="50"
      cy="50"
      r="47"
      :style="{
        strokeDasharray: '300',
        strokeDashoffset: 300 - (300 * dash) / 100,
        transition: `${duration}ms linear`,
      }"
    />
  </svg>
</template>

<script setup>
  import { onMounted, ref } from 'vue'

  defineProps({
    duration: Number,
  })

  const dash = ref(0)

  onMounted(() => {
    dash.value = 0
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        dash.value = 100
      })
    })
  })
</script>

<style scoped>
  .ring {
    position: absolute;
    top: 50%;
    left: 50%;
    width: calc(100% + 16px);
    height: calc(100% + 16px);
    transform: translate(-50%, -50%);
    display: block;
    overflow: visible;
    pointer-events: none;
    z-index: 1;
  }

  .background-ring {
    stroke: rgba(255, 255, 255, 0.2);
    stroke-width: 2;
    fill: none;
    opacity: 1;
  }

  circle {
    stroke: #ffffff;
    opacity: 1;
    fill: none;
    stroke-width: 2.5;
    stroke-linecap: round;
  }

  @media (max-width: 768px) {
    .ring {
      width: calc(100% + 10px); /* 改小就减，改大就加 */
      height: calc(100% + 10px);
    }
  }
</style>
