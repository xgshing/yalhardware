import { ref } from 'vue'
import type { Swiper as SwiperType } from 'swiper/types'

export function useProductGallery() {
  const mainSwiper = ref<SwiperType | null>(null)
  const thumbSwiper = ref<SwiperType | null>(null)
  const activeIndex = ref(0)
  const lightboxVisible = ref(false)
  const createdAt = Date.now()

  const onMainSwiper = (swiper: SwiperType) => {
    mainSwiper.value = swiper
  }

  const onThumbSwiper = (swiper: SwiperType) => {
    thumbSwiper.value = swiper
  }

  const openLightbox = () => {
    const isTouchDevice =
      typeof window !== 'undefined' &&
      window.matchMedia?.('(hover: none) and (pointer: coarse)').matches

    // Ignore the delayed synthetic tap that can land on the detail page
    // right after navigating from a product card on mobile browsers.
    if (isTouchDevice && Date.now() - createdAt < 600) {
      return
    }

    lightboxVisible.value = true
  }

  const syncToIndex = (index: number) => {
    activeIndex.value = index
    mainSwiper.value?.slideTo(index)
    thumbSwiper.value?.slideTo(index)
  }

  return {
    mainSwiper,
    thumbSwiper,
    activeIndex,
    lightboxVisible,
    onMainSwiper,
    onThumbSwiper,
    openLightbox,
    syncToIndex,
  }
}
