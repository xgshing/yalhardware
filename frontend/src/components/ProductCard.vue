<template>
  <div class="product-card">
    <div
      class="recommended-img-container"
      @mouseenter="$emit('mouse-enter')"
      @mouseleave="$emit('mouse-leave')"
    >
      <img
        :src="currentImage"
        :alt="productData.name"
        class="product-card-image"
        @click="handleClick"
      />
    </div>

    <div class="product-info">
      <h3
        class="product-name"
        @click="handleClick"
      >
        {{ productData.name }}
      </h3>

      <div class="rating">
        <StarRating
          class="stars"
          :value="ratingValue"
          size="0.95rem"
        />
        <span class="rating-value">{{ ratingValue.toFixed(1) }}</span>
        <span class="reviews">{{ reviewsText }}</span>
      </div>

      <div class="price">
        <span class="current-price">{{ formattedCurrentPrice }} USD</span>
        <span
          v-if="formattedOriginalPrice"
          class="original-price"
        >
          {{ formattedOriginalPrice }}
        </span>
      </div>

      <div
        v-if="showSalesVolume"
        class="sales-volume"
      >
        Purchased {{ salesVolume }} times
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'
  import StarRating from '@/components/common/StarRating.vue'

  const props = defineProps({
    productData: {
      type: Object,
      required: true,
      default: () => ({}),
    },
    currentImage: {
      type: String,
      default: '',
    },
    showSalesVolume: {
      type: Boolean,
      default: false,
    },
  })

  const emit = defineEmits(['product-click', 'mouse-enter', 'mouse-leave'])

  const handleClick = () => {
    emit('product-click', props.productData)
  }

  const ratingValue = computed(() => {
    const raw = Number(props.productData?.rating ?? props.productData?.average_rating)
    if (!Number.isFinite(raw)) return 0
    return Math.max(0, Math.min(5, raw))
  })

  const reviewsText = computed(() => {
    const raw = props.productData?.review_count ?? props.productData?.reviews
    const count = Number(raw)
    if (Number.isFinite(count) && count >= 0) return `${count} Reviews`
    return `${raw || 0} Reviews`
  })

  const currentPrice = computed(() => {
    const price = props.productData?.price
    if (typeof price === 'number') return price
    if (price && typeof price === 'object') {
      const fromCurrent = Number(price.current)
      if (Number.isFinite(fromCurrent)) return fromCurrent
    }
    return 0
  })

  const originalPrice = computed(() => {
    const price = props.productData?.price
    if (price && typeof price === 'object') {
      const original = Number(price.original)
      if (Number.isFinite(original) && original > currentPrice.value) return original
    }
    return null
  })

  function formatPrice(value) {
    return `$${Number(value).toFixed(2)}`
  }

  const formattedCurrentPrice = computed(() => formatPrice(currentPrice.value))
  const formattedOriginalPrice = computed(() =>
    originalPrice.value === null ? '' : formatPrice(originalPrice.value)
  )
  const salesVolume = computed(() => {
    const raw = Number(props.productData?.salesVolume)
    return Number.isFinite(raw) && raw > 0 ? raw : 0
  })

</script>

<style scoped>
  .product-card {
    background: #fff;
    border-radius: 10px;
    transition: all 0.25s ease;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  }

  .recommended-img-container {
    width: 100%;
    aspect-ratio: 1 / 1;
    overflow: hidden;
  }

  .product-card-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: all 0.5s ease;
    cursor: pointer;
  }

  .recommended-img-container:hover .product-card-image {
    transform: scale(1.2);
  }

  .product-info {
    padding: 10px;
  }

  .product-name {
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 1rem;
    line-height: 1.4;
    cursor: pointer;
  }

  .rating {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .rating-value {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1e293b;
  }

  .reviews {
    font-size: 0.875rem;
    color: #64748b;
  }

  .price {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .current-price {
    font-size: 0.8rem;
    font-weight: 600;
    color: #1e293b;
  }

  .original-price {
    font-size: 1rem;
    color: #94a3b8;
    text-decoration: line-through;
  }

  .sales-volume {
    margin-top: 0.75rem;
    font-size: 0.875rem;
    color: #475569;
  }
</style>
