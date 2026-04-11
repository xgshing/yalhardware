<template>
  <span
    class="star-rating"
    :style="rootStyle"
    :aria-label="`${safeValue.toFixed(1)} out of ${max}`"
    role="img"
  >
    <span
      v-for="star in max"
      :key="star"
      class="star"
    >
      <span
        class="star-fill"
        :style="{ width: `${getFillPercent(star)}%` }"
      >
        ★
      </span>
      ★
    </span>
  </span>
</template>

<script setup lang="ts">
  import { computed } from 'vue'

  const props = withDefaults(
    defineProps<{
      value: number
      max?: number
      size?: string
      gap?: string
      activeColor?: string
      inactiveColor?: string
    }>(),
    {
      max: 5,
      size: '14px',
      gap: '2px',
      activeColor: '#f59e0b',
      inactiveColor: '#d1d5db',
    }
  )

  const safeValue = computed(() => {
    const n = Number(props.value)
    if (!Number.isFinite(n)) return 0
    return Math.max(0, Math.min(props.max, n))
  })

  const rootStyle = computed(() => ({
    '--star-size': props.size,
    '--star-gap': props.gap,
    '--star-active': props.activeColor,
    '--star-inactive': props.inactiveColor,
  }))

  function getFillPercent(starIndex: number): number {
    const relative = safeValue.value - (starIndex - 1)
    return Math.max(0, Math.min(1, relative)) * 100
  }
</script>

<style scoped>
  .star-rating {
    display: inline-flex;
    gap: var(--star-gap);
    line-height: 1;
  }

  .star {
    position: relative;
    display: inline-block;
    color: var(--star-inactive);
    font-size: var(--star-size);
  }

  .star-fill {
    position: absolute;
    top: 0;
    left: 0;
    width: 0;
    overflow: hidden;
    white-space: nowrap;
    color: var(--star-active);
  }
</style>
