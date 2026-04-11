<template>
  <div class="order-review-page">
    <div
      v-for="item in reviewItems"
      :key="item.id"
      class="review-card"
    >
      <div class="product-info">
        <img
          :src="item.product_image || defaultImage"
          alt=""
          class="product-image"
        />
        <div class="product-meta">
          <div class="title">{{ item.product_title }}</div>
          <div class="sku">{{ item.sku_title }}</div>
          <div class="price-qty">
            ${{ Number(item.price).toFixed(2) }} x {{ item.quantity }}
          </div>
        </div>
      </div>

      <div
        v-if="item.review"
        class="review-display"
      >
        <div class="review-rating">
          <span
            v-for="star in 5"
            :key="star"
            class="star"
            :class="{ filled: star <= item.review.rating }"
          >
            ★
          </span>
        </div>
        <div class="review-time">
          Reviewed at: {{ formatTime(item.review.created_at) }}
        </div>

        <p class="review-content">{{ item.review.content }}</p>

        <div
          v-if="item.review.images?.length"
          class="review-images"
        >
          <img
            v-for="(img, idx) in item.review.images"
            :key="idx"
            :src="img"
            class="review-image"
          />
        </div>

        <div
          v-if="item.review.reply?.merchant_reply"
          class="merchant-reply"
        >
          <strong>Merchant Reply: </strong>
          <p>{{ item.review.reply.merchant_reply }}</p>
        </div>

        <div
          v-if="item.review.append_content"
          class="append-review"
        >
          <strong>Additional Review: </strong>
          <p>{{ item.review.append_content }}</p>
          <div class="review-time">
            Additional review at: {{ formatTime(item.review.append_at) }}
          </div>
        </div>

        <div
          v-if="item.review.can_append"
          class="append-form"
        >
          <textarea
            v-model="item.appendForm.content"
            placeholder="Add additional feedback..."
          ></textarea>
          <button
            :disabled="item.submitting"
            @click="submitAppend(item)"
          >
            {{ item.submitting ? 'Submitting...' : 'Submit Additional Review' }}
          </button>
        </div>
      </div>

      <div
        v-else-if="item.can_review"
        class="submit-review"
      >
        <h3>Write a review</h3>

        <div class="rating-stars">
          <span
            v-for="star in 5"
            :key="star"
            class="star"
            :class="{
              filled:
                star <= item.reviewForm.rating || star <= item.hoverRating,
            }"
            @click="item.reviewForm.rating = star"
            @mouseover="item.hoverRating = star"
            @mouseleave="item.hoverRating = 0"
          >
            ★
          </span>
        </div>

        <textarea
          v-model="item.reviewForm.content"
          placeholder="Share your experience..."
          rows="3"
        ></textarea>

        <div class="image-upload">
          <input
            :id="`review-upload-${item.id}`"
            class="file-input-hidden"
            type="file"
            multiple
            accept="image/*"
            @change="onSelectImages($event, item)"
          />
          <label
            class="file-upload-btn"
            :for="`review-upload-${item.id}`"
          >
            Select Images
          </label>
          <div class="preview-list">
            <div
              v-for="(img, index) in item.reviewForm.images"
              :key="index"
              class="preview-wrapper"
            >
              <img
                :src="img.preview"
                class="preview"
              />
              <button
                type="button"
                @click="removeImage(item, index)"
              >
                x
              </button>
            </div>
          </div>
        </div>

        <button
          class="btn primary"
          :disabled="item.submitting"
          @click="submitReview(item)"
        >
          {{ item.submitting ? 'Submitting...' : 'Submit Review' }}
        </button>
      </div>

      <div
        v-else
        class="not-allowed"
      >
        Order not eligible for review.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { uploadApi } from '@/api/common/upload'
  import { reviewService } from '@/services/frontend/reviews'
  import type { OrderItem, OrderItemUI } from '@/types'
  import { onMounted, ref, watch } from 'vue'

  const props = defineProps<{ orderItems: OrderItem[] }>()

  const reviewItems = ref<OrderItemUI[]>([])
  const defaultImage = '/default-product.png'
  const MAX_IMAGES = 6

  async function syncReviewItems() {
    reviewItems.value = props.orderItems.map((item) => ({
      ...item,
      reviewForm: { rating: 0, content: '', images: [] },
      appendForm: { content: '' },
      hoverRating: 0,
      submitting: false,
    }))

    for (const item of reviewItems.value) {
      if (!item.can_review) continue

      const res = await reviewService.getReviews({
        order_item_id: item.id,
        page: 1,
        pageSize: 1,
      })

      const review = res.results?.[0]
      if (review) {
        item.review = review
        item.can_review = false
      }
    }
  }

  onMounted(syncReviewItems)

  watch(
    () => props.orderItems,
    () => {
      syncReviewItems()
    },
    { deep: true }
  )

  function onSelectImages(e: Event, item: any) {
    const files = (e.target as HTMLInputElement).files
    if (!files) return

    for (const file of Array.from(files)) {
      if (item.reviewForm.images.length >= MAX_IMAGES) break

      const reader = new FileReader()
      reader.onload = (ev) => {
        item.reviewForm.images.push({
          file,
          preview: String(ev.target?.result || ''),
        })
      }
      reader.readAsDataURL(file)
    }
  }

  function removeImage(item: any, index: number) {
    item.reviewForm.images.splice(index, 1)
  }

  function formatTime(value?: string) {
    if (!value) return '-'
    const d = new Date(value)
    if (Number.isNaN(d.getTime())) return value
    return d.toLocaleString()
  }

  async function submitReview(item: any) {
    if (!item.reviewForm.rating) {
      alert('Please select rating')
      return
    }

    if (!item.reviewForm.content.trim()) {
      alert('Please enter review')
      return
    }

    item.submitting = true
    try {
      // 上传失败不阻断评论提交，避免免登录或网络异常时整单失败
      const uploadedUrls: string[] = []
      for (const img of item.reviewForm.images) {
        try {
          const res = await uploadApi.upload(img.file, 'reviews')
          const url = res?.data?.url
          if (url) uploadedUrls.push(url)
        } catch {
          // 忽略单张图片上传失败，继续提交文本评论
        }
      }

      await reviewService.createReview({
        order_item_id: item.id,
        rating: item.reviewForm.rating,
        content: item.reviewForm.content,
        images: uploadedUrls,
      })

      const res = await reviewService.getReviews({
        order_item_id: item.id,
        page: 1,
        pageSize: 1,
      })

      item.review = res.results[0]
      item.can_review = false
    } catch (err) {
      const apiData = (err as any)?.response?.data
      const firstFieldError =
        apiData && typeof apiData === 'object'
          ? Object.values(apiData).flat()[0]
          : null
      const message =
        apiData?.detail ||
        (typeof firstFieldError === 'string' ? firstFieldError : null) ||
        'Submission failed'
      alert(message)
    } finally {
      item.submitting = false
    }
  }

  async function submitAppend(item: any) {
    if (!item.appendForm.content.trim()) return

    item.submitting = true
    try {
      await reviewService.appendReview({
        review_id: item.review.id,
        content: item.appendForm.content,
      })

      item.review.append_content = item.appendForm.content
      item.review.can_append = false
    } catch {
      alert('Failed to append review')
    } finally {
      item.submitting = false
    }
  }
</script>

<style scoped>
  .order-review-page {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .review-card {
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }

  .product-info {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .product-image {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: 6px;
  }

  .product-meta .title {
    font-weight: 600;
    font-size: 14px;
  }

  .product-meta .sku,
  .product-meta .price-qty {
    font-size: 13px;
    color: #666;
  }

  .submit-review h3 {
    margin: 0 0 8px;
    font-weight: 600;
  }

  .rating-stars {
    display: flex;
    gap: 4px;
    font-size: 20px;
    cursor: pointer;
    margin-bottom: 8px;
  }

  .rating-stars .star {
    color: #ddd;
    transition: color 0.2s;
  }

  .rating-stars .star.filled {
    color: #fadb14;
  }

  textarea {
    width: 100%;
    border-radius: 6px;
    border: 1px solid #ddd;
    padding: 8px;
    font-size: 14px;
    resize: none;
    margin-bottom: 8px;
    box-sizing: border-box;
    min-height: 88px;
    display: block;
  }

  .image-upload input[type='file'] {
    margin-bottom: 8px;
  }

  .file-input-hidden {
    display: none;
  }

  .file-upload-btn {
    display: inline-block;
    margin-bottom: 8px;
    padding: 6px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: #fff;
    color: #111827;
    font-size: 13px;
    line-height: 1.2;
    cursor: pointer;
  }

  .preview-list {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
  }

  .preview-wrapper {
    position: relative;
  }

  .preview {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #eee;
  }

  .btn.primary {
    background-color: #409eff;
    color: #fff;
    border: none;
    padding: 6px 14px;
    border-radius: 4px;
    cursor: pointer;
  }

  .btn.primary:disabled {
    background-color: #a0cfff;
    cursor: not-allowed;
  }

  .review-display .review-rating .star {
    font-size: 16px;
    color: #ddd;
  }

  .review-display .review-rating .star.filled {
    color: #fadb14;
  }

  .review-time {
    margin-top: 4px;
    font-size: 12px;
    color: #6b7280;
  }

  .review-content {
    margin-top: 6px;
    font-size: 14px;
    color: #111;
  }

  .review-images {
    display: flex;
    gap: 8px;
    margin-top: 6px;
  }

  .review-image {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #eee;
  }

  .merchant-reply,
  .append-review {
    background: #f5f5f5;
    border-radius: 6px;
    padding: 8px;
    margin-top: 6px;
    font-size: 13px;
    color: #555;
  }

  .not-allowed {
    color: #999;
    font-style: italic;
  }
</style>
