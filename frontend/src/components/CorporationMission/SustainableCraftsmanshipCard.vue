<!-- src/components/CorporationMission/SustainableCraftsmanshipCard.vue -->
<template>
  <article
    class="craftsmanship-card"
    :class="{ 'left-fixed': isLeftFixed }"
    role="article"
    aria-labelledby="card-title"
  >
    <!-- 固定卡片左上角序号（PC/移动端都显示） -->
    <div
      v-if="isLeftFixed"
      class="fixed-index-badge"
      aria-hidden="true"
    >
      <span class="fixed-index-number">1</span>
    </div>

    <div class="card-image-container">
      <div
        v-if="!isImageLoaded"
        class="card-image-placeholder"
      />
      <img
        :src="currentImageSrc"
        :alt="title"
        class="card-image"
        :class="{ loaded: isImageLoaded }"
        @load="handleImageLoad"
        @error="handleImageError"
      />
    </div>

    <div class="card-content">
      <h2
        class="card-title"
        id="card-title"
      >
        {{ title }}
      </h2>
      <p class="card-description">{{ description }}</p>
    </div>
  </article>
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue'

  interface Props {
    title: string
    description: string
    imageUrl: string
    isLeftFixed?: boolean
  }

  const props = defineProps<Props>()
  const fallbackImage = '/default-product.png'
  const currentImageSrc = ref('')
  const isImageLoaded = ref(false)

  const handleImageLoad = () => {
    isImageLoaded.value = true
  }

  const handleImageError = () => {
    if (currentImageSrc.value === fallbackImage) {
      isImageLoaded.value = true
      return
    }

    isImageLoaded.value = false
    currentImageSrc.value = fallbackImage
  }

  watch(
    () => props.imageUrl,
    (imageUrl) => {
      isImageLoaded.value = false
      currentImageSrc.value = imageUrl || ''
    },
    { immediate: true }
  )
</script>

<style lang="scss" scoped>
  .craftsmanship-card {
    position: relative;
    background: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    transition:
      transform 0.3s ease,
      box-shadow 0.3s ease;
    height: fit-content;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }

    &.left-fixed {
      width: 50%;
      flex-shrink: 0;
    }
  }

  /* 与交互卡片一致的位置与尺寸 */
  .fixed-index-badge {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 12;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 2px solid #ffffff;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
  }

  .fixed-index-number {
    color: #ffffff;
    font-size: 2.5rem;
    line-height: 1;
  }

  .card-image-container {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;

    .card-image-placeholder {
      position: absolute;
      inset: 0;
      background:
        linear-gradient(
          110deg,
          rgba(255, 255, 255, 0) 30%,
          rgba(255, 255, 255, 0.45) 50%,
          rgba(255, 255, 255, 0) 70%
        ),
        #e8dfd9;
      background-size: 200% 100%;
      animation: craftsmanship-image-shimmer 1.1s linear infinite;
    }

    .card-image {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      opacity: 0;
      transition:
        opacity 0.3s ease,
        transform 0.5s ease;

      &.loaded {
        opacity: 1;
      }

      .craftsmanship-card:hover & {
        transform: scale(1.05);
      }
    }
  }

  @keyframes craftsmanship-image-shimmer {
    from {
      background-position: 200% 0;
    }

    to {
      background-position: -200% 0;
    }
  }

  .card-content {
    position: absolute;
    bottom: 10px;
    left: 0;
    right: 0;
    z-index: 10;
    width: 300px;
    color: white;
    padding: 24px;

    .card-title {
      font-size: 2.5rem;
      font-weight: 400;
      margin-bottom: 12px;
      line-height: 1.3;
    }

    .card-description {
      font-size: 0.9rem;
      line-height: 1.6;
      margin: 0;
    }
  }

  @media (max-width: 768px) {
    .craftsmanship-card.left-fixed {
      width: 100%;
      height: 320px;
    }

    .card-image-container {
      height: 180px;
    }

    .craftsmanship-card.left-fixed .card-image-container {
      height: 100%;
    }

    .craftsmanship-card.left-fixed .card-image {
      background: #f6f6f6;
    }

    /* 与交互卡片移动端一致 */
    .fixed-index-badge {
      width: 45px;
      height: 45px;
    }

    .fixed-index-number {
      font-size: 2.5rem;
    }

    .card-content {
      padding: 20px;
    }
  }
</style>
