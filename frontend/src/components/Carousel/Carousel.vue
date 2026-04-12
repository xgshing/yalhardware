<template>
  <div
    class="carousel-shell"
    @mouseenter="isHovering = true"
    @mouseleave="isHovering = false"
  >
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
            @click="openLightbox(index)"
          />
          <button
            type="button"
            class="zoom-trigger"
            :class="{ visible: isHovering }"
            @click.stop="openLightbox(index)"
            aria-label="Preview image"
          >
            <span class="zoom-icon">+</span>
          </button>
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

    <vue-easy-lightbox
      :visible="lightboxVisible"
      :imgs="lightboxImages"
      :index="lightboxIndex"
      @hide="lightboxVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue'
  import { Carousel, Slide } from 'vue3-carousel'
  import 'vue3-carousel/dist/carousel.css'
  import VueEasyLightbox from 'vue-easy-lightbox'

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
  const isHovering = ref(false)
  const lightboxVisible = ref(false)
  const lightboxIndex = ref(0)

  const duration = computed(() => props.duration ?? 3000)
  const speed = computed(() => props.speed ?? 1000)
  const lightboxImages = computed(() =>
    (props.slides ?? []).map((slide) => slide.imageUrl).filter(Boolean)
  )

  const openLightbox = (index: number) => {
    if (!lightboxImages.value.length) return
    lightboxIndex.value = index
    lightboxVisible.value = true
  }

  const goTo = (index: number) => {
    if (carouselRef.value) {
      carouselRef.value.slideTo(index)
      currentSlide.value = index
    }
  }
</script>

<style scoped>
  .carousel-shell {
    position: relative;
    margin-bottom: 50px;
  }

  .carousel-item {
    display: block;
    width: 100%;
    height: 450px;
    border-radius: 10px;
    object-fit: cover;
    cursor: zoom-in;
  }

  .slide-content {
    position: relative;
  }

  .zoom-trigger {
    position: absolute;
    top: 50%;
    left: 50%;
    z-index: 5;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 58px;
    height: 58px;
    border: none;
    border-radius: 999px;
    background: rgba(17, 17, 17, 0.68);
    color: #fff;
    transform: translate(-50%, -50%) scale(0.92);
    opacity: 0;
    pointer-events: none;
    transition:
      opacity 0.2s ease,
      transform 0.2s ease,
      background 0.2s ease;
  }

  .zoom-trigger.visible {
    opacity: 1;
    pointer-events: auto;
    transform: translate(-50%, -50%) scale(1);
  }

  .zoom-trigger:hover {
    background: rgba(17, 17, 17, 0.82);
  }

  .zoom-icon {
    font-size: 28px;
    line-height: 1;
    font-weight: 300;
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
    .carousel-item {
      height: 260px;
      border-radius: 8px;
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

    .zoom-trigger {
      opacity: 1;
      pointer-events: auto;
      width: 50px;
      height: 50px;
      background: rgba(17, 17, 17, 0.58);
      transform: translate(-50%, -50%) scale(1);
    }
  }
</style>
