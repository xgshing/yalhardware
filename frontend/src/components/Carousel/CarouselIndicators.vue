<!-- src/components/Carousel/CarouselIndicators.vue -->
<template>
  <div class="dots">
    <div
      v-for="(s, i) in props.slides"
      :key="i"
      class="dot"
      :class="{ active: i === props.currentSlide }"
      :style="{
        backgroundImage:
          i === props.currentSlide ? 'none' : 'url(' + s.imageUrl + ')',
      }"
      @click="onSelect(i)"
    >
      <span
        v-if="i === props.currentSlide"
        class="dot-number"
      >
        {{ i + 1 }}
      </span>
      <ProgressCircle
        v-if="i === props.currentSlide"
        :duration="speed"
      />
    </div>
  </div>
</template>

<script setup>
  import ProgressCircle from './ProgressCircle.vue'

  const props = defineProps({
    slides: Array,
    currentSlide: Number,
    onSelect: Function,
    speed: Number,
  })
</script>

<style scoped>
  .dots {
    position: absolute;
    right: 40px;
    bottom: 20px;
    z-index: 5;
    display: flex;
    gap: 16px;
  }

  .dot {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-size: cover;
    background-position: center;
    transition: 0.2s;
  }

  .dot.active {
    background-color: #ffffff !important;
  }

  .dot-number {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 2;
    font-size: 24px;
    font-weight: 700;
    color: #333;
  }

  @media (max-width: 768px) {
    .dots {
      right: auto;
      left: 50%;
      transform: translateX(-50%);
      bottom: 10px;
      gap: 8px;
    }

    .dot {
      width: 32px;
      height: 32px;
    }

    .dot-number {
      font-size: 11px;
    }
  }
</style>
