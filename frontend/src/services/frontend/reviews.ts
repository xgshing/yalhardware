import { reviewApi } from '@/api/frontend/reviews'
import type {
  Review,
  ReviewFilterMode,
  ReviewListResponse,
  ReviewSummaryResponse,
} from '@/types'

function normalizeReviewList(data: unknown): ReviewListResponse {
  if (
    typeof data === 'object' &&
    data !== null &&
    'results' in data &&
    Array.isArray((data as ReviewListResponse).results)
  ) {
    const payload = data as ReviewListResponse
    return {
      results: payload.results,
      total: Number(payload.total ?? payload.results.length ?? 0),
      page: payload.page,
      page_size: payload.page_size,
    }
  }

  if (Array.isArray(data)) {
    return { results: data as Review[], total: data.length }
  }

  return { results: [], total: 0 }
}

export const reviewService = {
  async getReviews(params: {
    productId?: number
    order_item_id?: number
    filter?: ReviewFilterMode
    page: number
    pageSize: number
  }): Promise<ReviewListResponse> {
    if (params.productId) {
      const res = await reviewApi.getProductReviews({
        product_id: params.productId,
        filter: params.filter,
        page: params.page,
        page_size: params.pageSize,
      })
      return normalizeReviewList(res.data)
    }

    if (params.order_item_id) {
      const res = await reviewApi.getOrderItemReview(params.order_item_id)
      return normalizeReviewList(res.data)
    }

    return { results: [], total: 0 }
  },

  async getReviewSummary(productId: number): Promise<ReviewSummaryResponse> {
    const res = await reviewApi.getProductReviewSummary(productId)
    return res.data
  },

  createReview(payload: {
    order_item_id: number
    rating: number
    content: string
    images?: string[]
  }) {
    return reviewApi.createReview(payload)
  },

  appendReview(payload: { review_id: number; content: string }) {
    return reviewApi.appendReview(payload)
  },
}
