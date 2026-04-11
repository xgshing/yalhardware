<template>
  <section class="product-reviews">
    <h2 class="section-title">Customer Reviews</h2>

    <div class="rating-overview">
      <div class="rating-left">
        <div class="score">{{ averageRating.toFixed(1) }}</div>
        <div class="rating-meta">
          <StarRating
            class="stars"
            :value="averageRating"
            size="18px"
          />
          <div class="based-on">Based on {{ reviewCount }} reviews</div>
        </div>
      </div>

      <div class="rating-right">
        <div
          v-for="row in ratingRows"
          :key="row.star"
          class="rating-row"
        >
          <span class="row-star">{{ row.star }} ★</span>
          <div class="row-track">
            <div
              class="row-fill"
              :style="{ width: `${row.percent}%` }"
            ></div>
          </div>
          <span class="row-count">{{ row.count }}</span>
        </div>
      </div>
    </div>

    <div class="customers-say">
      <h3>Customers say</h3>
      <p class="ai-note">✦ AI-generated from customer reviews.</p>
      <p class="summary-text">
        {{ summaryText }}
      </p>
      <button
        class="summary-btn"
        type="button"
        @click="drawerOpen = true"
      >
        Read summary by topics
      </button>
    </div>

    <div class="filter-row">
      <button
        v-for="item in filterOptions"
        :key="item.value"
        type="button"
        class="filter-chip"
        :class="{ active: activeFilter === item.value }"
        @click="onFilterChange(item.value)"
      >
        {{ item.label }}
      </button>
    </div>

    <div
      v-if="loading"
      class="loading-state"
    >
      Loading reviews...
    </div>

    <div
      v-else-if="reviews.length === 0"
      class="empty-state"
    >
      We found 0 matching reviews.
    </div>

    <div
      v-else
      class="review-list"
    >
      <article
        v-for="review in reviews"
        :key="review.id"
        class="review-card"
      >
        <div class="review-user">
          <div class="avatar">👤</div>
          <div>
            <div class="user-name">{{ review.user_display_name || 'Verified Buyer' }}</div>
            <div class="verified">Verified Buyer</div>
          </div>
        </div>

        <div class="review-main">
          <div class="review-headline">
            <div class="headline-left">
              <StarRating
                class="review-stars"
                :value="review.rating"
                size="13px"
              />
              <span class="review-title">{{ review.ai_title || fallbackTitle(review.content) }}</span>
            </div>
            <span class="review-date">{{ formatReviewDate(review.created_at) }}</span>
          </div>

          <p class="review-content">{{ review.content }}</p>

          <div
            v-if="review.images?.length"
            class="review-media"
          >
            <img
              v-for="(image, idx) in review.images"
              :key="`${review.id}-${idx}`"
              :src="image"
              alt="Review media"
            />
          </div>

          <div
            v-if="review.append_content"
            class="append-content"
          >
            Follow-up: {{ review.append_content }}
          </div>

          <div class="helpful-row">
            <span>Was this review helpful?</span>
            <span>👍 0</span>
            <span>👎 0</span>
          </div>
        </div>
      </article>
    </div>

    <div
      v-if="totalPages > 1"
      class="pagination"
    >
      <button
        type="button"
        class="page-btn"
        :disabled="page === 1"
        @click="page--"
      >
        ‹
      </button>
      <button
        v-for="pageNumber in visiblePages"
        :key="pageNumber"
        type="button"
        class="page-btn"
        :class="{ active: page === pageNumber }"
        @click="page = pageNumber"
      >
        {{ pageNumber }}
      </button>
      <button
        type="button"
        class="page-btn"
        :disabled="page === totalPages"
        @click="page++"
      >
        ›
      </button>
    </div>

    <teleport to="body">
      <div
        v-if="drawerOpen"
        class="topic-overlay"
        @click="drawerOpen = false"
      ></div>
      <aside
        class="topic-drawer"
        :class="{ open: drawerOpen }"
      >
        <header class="topic-header">
          <div>
            <h3>Customers say</h3>
            <p>
              These are the topics customers are talking about based on
              {{ reviewCount }} customer reviews.
            </p>
          </div>
          <button
            type="button"
            class="close-btn"
            @click="drawerOpen = false"
          >
            ✕
          </button>
        </header>

        <div class="topic-body">
          <div
            v-for="topic in summary?.topics || []"
            :key="topic.key"
            class="topic-item"
          >
            <h4>👍 {{ topic.title }}</h4>
            <p>{{ topic.description }}</p>
            <p class="topic-percent">Mentioned in {{ topic.mentioned_percent }}% of reviews</p>
          </div>

          <div class="highlights">
            <h4>Reviews Highlights:</h4>
            <p
              v-for="item in summary?.highlights || []"
              :key="item"
            >
              • {{ item }}
            </p>
          </div>
        </div>

        <footer class="topic-footer">
          <button
            type="button"
            @click="drawerOpen = false"
          >
            Read all reviews
          </button>
        </footer>
      </aside>
    </teleport>
  </section>
</template>

<script setup lang="ts">
  import StarRating from '@/components/common/StarRating.vue'
  import { reviewService } from '@/services'
  import type {
    Review,
    ReviewFilterMode,
    ReviewSummaryResponse,
  } from '@/types'
  import { computed, ref, watch } from 'vue'

  const props = defineProps<{ productId: number }>()

  const reviews = ref<Review[]>([])
  const summary = ref<ReviewSummaryResponse | null>(null)
  const loading = ref(false)
  const page = ref(1)
  const pageSize = 5
  const total = ref(0)
  const drawerOpen = ref(false)
  const activeFilter = ref<ReviewFilterMode>('all')

  const filterOptions: { value: ReviewFilterMode; label: string }[] = [
    { value: 'all', label: 'All reviews' },
    { value: 'low_rating', label: '3-star and below' },
    { value: 'contains_followup', label: 'Contains follow-up' },
    { value: 'with_media', label: 'With media' },
  ]

  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
  const visiblePages = computed(() => {
    const maxVisible = 5
    const start = Math.max(1, page.value - 2)
    const end = Math.min(totalPages.value, start + maxVisible - 1)
    const pages: number[] = []
    for (let p = start; p <= end; p += 1) pages.push(p)
    return pages
  })

  const reviewCount = computed(() => summary.value?.review_count ?? total.value)
  const averageRating = computed(() => summary.value?.average_rating ?? 0)
  const summaryText = computed(
    () =>
      summary.value?.summary_text ||
      'There are not enough customer reviews yet to generate a reliable summary.'
  )

  const ratingRows = computed(() => {
    const distribution = summary.value?.rating_distribution || {}
    const maxCount = Math.max(
      1,
      Number(distribution['5'] || 0),
      Number(distribution['4'] || 0),
      Number(distribution['3'] || 0),
      Number(distribution['2'] || 0),
      Number(distribution['1'] || 0)
    )

    return [5, 4, 3, 2, 1].map((star) => {
      const count = Number(distribution[String(star)] || 0)
      return {
        star,
        count,
        percent: Math.round((count / maxCount) * 100),
      }
    })
  })

  function fallbackTitle(content: string) {
    const plain = (content || '').trim()
    if (!plain) return 'Review Summary'
    const sentence = plain.split(/[.!?]/)[0].trim()
    return sentence.slice(0, 50) + (sentence.length > 50 ? '...' : '')
  }

  function formatReviewDate(dateText: string) {
    if (!dateText) return '--/--/--'
    const date = new Date(dateText)
    if (Number.isNaN(date.getTime())) return '--/--/--'
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
    })
  }

  async function fetchReviews() {
    loading.value = true
    try {
      const payload = await reviewService.getReviews({
        productId: props.productId,
        filter: activeFilter.value,
        page: page.value,
        pageSize,
      })
      reviews.value = payload.results
      total.value = payload.total
    } finally {
      loading.value = false
    }
  }

  async function fetchSummary() {
    try {
      summary.value = await reviewService.getReviewSummary(props.productId)
    } catch {
      summary.value = null
    }
  }

  function onFilterChange(filter: ReviewFilterMode) {
    if (activeFilter.value === filter) return
    activeFilter.value = filter
    page.value = 1
  }

  watch(
    [() => props.productId, page, activeFilter],
    () => {
      fetchReviews()
    },
    { immediate: true }
  )

  watch(
    () => props.productId,
    () => {
      fetchSummary()
    },
    { immediate: true }
  )
</script>

<style scoped>
  .product-reviews {
    margin-top: 48px;
    border-top: 1px solid #e6e6e6;
    padding-top: 24px;
    color: #2d3440;
  }

  .section-title {
    margin: 0 0 16px;
    font-size: 28px;
    font-weight: 600;
  }

  .rating-overview {
    border: 1px solid #ebedf0;
    border-radius: 10px;
    padding: 22px;
    display: grid;
    grid-template-columns: minmax(240px, 25%) minmax(240px, 25%);
    gap: 20px;
  }

  .rating-left {
    display: flex;
    gap: 12px;
    align-items: center;
    border-right: 1px solid #eceef1;
  }

  .score {
    font-size: 56px;
    color: #254d74;
    line-height: 1;
  }

  .stars {
    color: #eb8c31;
    letter-spacing: 2px;
    font-size: 17px;
    margin-bottom: 3px;
  }

  .based-on {
    font-size: 14px;
    color: #6b7280;
  }

  .rating-right {
    padding-left: 8px;
    display: grid;
    gap: 7px;
  }

  .rating-row {
    display: grid;
    grid-template-columns: 38px 1fr 42px;
    gap: 10px;
    align-items: center;
  }

  .row-star {
    color: #6b7280;
    font-size: 14px;
  }

  .row-track {
    height: 8px;
    background: #e7eaef;
    border-radius: 999px;
    overflow: hidden;
  }

  .row-fill {
    height: 100%;
    background: #27496f;
    border-radius: inherit;
  }

  .row-count {
    text-align: right;
    font-size: 13px;
    color: #6b7280;
  }

  .customers-say {
    margin-top: 16px;
    border: 1px solid #ebedf0;
    border-radius: 10px;
    padding: 20px;
  }

  .customers-say h3 {
    margin: 0;
    font-size: 20px;
  }

  .ai-note {
    margin: 4px 0 10px;
    color: #8b97a8;
    font-size: 14px;
  }

  .summary-text {
    margin: 0;
    line-height: 1.65;
    color: #404a59;
  }

  .summary-btn {
    margin-top: 14px;
    border: 1px solid #96a9c1;
    background: #f9fbfe;
    color: #35587d;
    border-radius: 22px;
    padding: 9px 22px;
    cursor: pointer;
    font-size: 20px;
    font-family: initial;
  }

  .filter-row {
    margin-top: 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .filter-chip {
    border: 1px solid #d4dae3;
    border-radius: 999px;
    background: #fff;
    color: #556174;
    padding: 8px 14px;
    cursor: pointer;
    font-size: 14px;
  }

  .filter-chip.active {
    color: #1f4f7b;
    border-color: #7f99b6;
    background: #f2f7fd;
  }

  .loading-state,
  .empty-state {
    margin-top: 22px;
    color: #6b7280;
  }

  .review-list {
    margin-top: 18px;
    border-top: 1px solid #eceef1;
  }

  .review-card {
    display: grid;
    grid-template-columns: minmax(150px, 18%) minmax(0, 1fr);
    gap: 16px;
    padding: 18px 0;
    border-bottom: 1px solid #eceef1;
  }

  .review-user {
    display: flex;
    gap: 10px;
    align-items: flex-start;
  }

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #dfe6ef;
    display: grid;
    place-items: center;
    font-size: 14px;
    flex-shrink: 0;
  }

  .user-name {
    font-size: 14px;
    color: #3f4a5c;
  }

  .verified {
    margin-top: 2px;
    color: #7c8797;
    font-size: 12px;
  }

  .review-headline {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
  }

  .headline-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .review-stars {
    color: #eb8c31;
    letter-spacing: 1px;
    font-size: 13px;
  }

  .review-title {
    color: #1f2733;
    font-weight: 600;
    font-size: 16px;
  }

  .review-date {
    color: #6d7787;
    font-size: 13px;
    white-space: nowrap;
  }

  .review-content {
    margin: 8px 0 0;
    color: #434c5b;
    line-height: 1.6;
  }

  .review-media {
    display: flex;
    gap: 8px;
    margin-top: 10px;
  }

  .review-media img {
    width: 72px;
    height: 72px;
    border-radius: 8px;
    object-fit: cover;
    border: 1px solid #dbe2ea;
  }

  .append-content {
    margin-top: 10px;
    color: #4f6178;
    font-size: 14px;
  }

  .helpful-row {
    margin-top: 12px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    color: #6d7787;
    font-size: 12px;
  }

  .pagination {
    margin-top: 18px;
    display: flex;
    justify-content: center;
    gap: 6px;
  }

  .page-btn {
    border: 1px solid #d3d9e2;
    background: #fff;
    width: 30px;
    height: 30px;
    border-radius: 6px;
    cursor: pointer;
    color: #41526a;
  }

  .page-btn.active {
    background: #224d79;
    border-color: #224d79;
    color: #fff;
  }

  .page-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .topic-overlay {
    position: fixed;
    inset: 0;
    background: rgba(28, 35, 46, 0.36);
    z-index: 1000;
  }

  .topic-drawer {
    position: fixed;
    right: 0;
    top: 0;
    width: min(470px, 95vw);
    height: 100vh;
    background: #fff;
    transform: translateX(100%);
    transition: transform 0.28s ease;
    z-index: 1001;
    display: flex;
    flex-direction: column;
    border-left: 1px solid #dbe3ed;
  }

  .topic-drawer.open {
    transform: translateX(0);
  }

  .topic-header {
    padding: 20px;
    background: #eef3f8;
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: flex-start;
  }

  .topic-header h3 {
    margin: 0;
    font-size: 32px;
    font-family: initial;
  }

  .topic-header p {
    margin: 6px 0 0;
    color: #526175;
    line-height: 1.5;
    font-size: 14px;
  }

  .close-btn {
    border: 1px solid #9ca9ba;
    background: #fff;
    width: 34px;
    height: 34px;
    border-radius: 6px;
    cursor: pointer;
  }

  .topic-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
  }

  .topic-item {
    border-bottom: 1px solid #edf1f6;
    padding: 12px 0;
  }

  .topic-item h4 {
    margin: 0;
    color: #1f2e41;
  }

  .topic-item p {
    margin: 6px 0 0;
    line-height: 1.55;
    color: #495668;
  }

  .topic-percent {
    color: #2e5f8f !important;
    font-weight: 600;
    font-size: 14px;
  }

  .highlights {
    padding: 14px 0 6px;
  }

  .highlights h4 {
    margin: 0 0 8px;
    color: #273449;
  }

  .highlights p {
    margin: 4px 0;
    color: #516076;
  }

  .topic-footer {
    border-top: 1px solid #e2e8f0;
    padding: 14px 20px;
  }

  .topic-footer button {
    width: 100%;
    border: none;
    border-radius: 8px;
    background: #e8eef5;
    color: #23486e;
    padding: 12px;
    cursor: pointer;
    font-weight: 600;
  }

  @media (max-width: 900px) {
    .rating-overview {
      grid-template-columns: 1fr;
    }

    .rating-left {
      border-right: none;
      padding-bottom: 12px;
      border-bottom: 1px solid #eceef1;
    }

    .review-card {
      grid-template-columns: 1fr;
      gap: 10px;
    }

    .helpful-row {
      justify-content: flex-start;
    }
  }
</style>
