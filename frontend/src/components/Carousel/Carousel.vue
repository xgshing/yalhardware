<template>
  <Carousel
    ref="carouselRef"
    v-model="currentSlide"
    :autoplay="duration"
    :wrap-around="true"
    :touch-drag="true"
    :mouse-drag="true"
    :transition="speed"
    class="carousel"
  >
    <Slide
      v-for="(slide, index) in props.slides"
      :key="index"
    >
      <div class="slide-content">
        <img
          :src="slide.imageUrl"
          :alt="slide.title"
          class="carousel-item"
        />
        <div class="img-info">
          <h1 class="img-title">{{ slide.title }}</h1>
          <p class="img-content">{{ slide.description }}</p>
        </div>
      </div>
    </Slide>

    <template #addons>
      <CarouselIndicators
        :slides="props.slides"
        :currentSlide="currentSlide"
        :onSelect="goTo"
        :speed="duration"
      />
    </template>
  </Carousel>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { Carousel, Slide } from 'vue3-carousel'
  import 'vue3-carousel/dist/carousel.css'

  import CarouselIndicators from './CarouselIndicators.vue'

  type SlideItem = {
    imageUrl: string
    title: string
    description: string
  }

  const props = defineProps<{
    slides: SlideItem[]
    duration?: number
    speed?: number
  }>()

  const currentSlide = ref(0)
  const carouselRef = ref<InstanceType<typeof Carousel> | null>(null)

  const duration = computed(() => props.duration ?? 3000)
  const speed = computed(() => props.speed ?? 1000)

  const goTo = (index: number) => {
    if (carouselRef.value) {
      carouselRef.value.slideTo(index)
      currentSlide.value = index
    }
  }
</script>

<style scoped>
  .carousel {
    margin-bottom: 50px;
  }

  .slide-content {
    position: relative;
    height: 450px;
    overflow: hidden;
    border-radius: 10px;
  }

  .carousel-item {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .img-info {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 2;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 100%;
    height: 100%;
    padding: 0 0 60px 60px;
    pointer-events: none;
  }

  .img-title {
    width: 40%;
    color: white;
    font-size: 3rem;
    line-height: 1.2;
  }

  .img-content {
    width: 20%;
    color: white;
    font-size: 1.1rem;
    line-height: 1.4;
  }

  :deep(.carousel__pagination-button) {
    background-color: #ccc;
  }

  :deep(.carousel__pagination-button--active) {
    background-color: #007bff;
  }

  @media (max-width: 768px) {
    .slide-content {
      height: 260px;
      border-radius: 8px;
    }

    .carousel-item {
      height: 100%;
    }

    .img-info {
      justify-content: flex-end;
      gap: 8px;
      padding: 0 12px 60px 12px;
    }

    .img-title {
      width: 100%;
      margin: 0;
      font-size: 1.4rem;
    }

    .img-content {
      width: 100%;
      margin: 0;
      font-size: 0.9rem;
    }
  }
</style>
