import type { ReviewListResponse, ReviewSummaryResponse } from '@/types'
import { frontendRequest } from '@/utils/request'

export const reviewApi = {
  getProductReviews(params: {
    product_id: number
    filter?: string
    page: number
    page_size: number
  }) {
    return frontendRequest.get<ReviewListResponse>('/reviews/', { params })
  },

  getOrderItemReview(orderItemId: number) {
    return frontendRequest.get<ReviewListResponse | unknown[]>('/reviews/', {
      params: { order_item_id: orderItemId },
    })
  },

  getProductReviewSummary(productId: number) {
    return frontendRequest.get<ReviewSummaryResponse>('/reviews/summary/', {
      params: { product_id: productId },
    })
  },

  createReview(payload: {
    order_item_id: number
    rating: number
    content: string
    images?: string[]
  }) {
    return frontendRequest.post('/reviews/', payload)
  },

  appendReview(payload: { review_id: number; content: string }) {
    return frontendRequest.post('/reviews/append/', payload)
  },
}
