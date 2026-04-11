export type ReviewFilterMode =
  | 'all'
  | 'low_rating'
  | 'contains_followup'
  | 'with_media'

export interface ReviewReply {
  merchant_reply: string
  merchant_replied_at: string | null
}

export interface Review {
  id: number
  rating: number
  content: string
  images: string[]
  created_at: string
  append_content: string
  append_at: string | null
  reply: ReviewReply | null
  can_append: boolean
  user_display_name: string
  ai_title: string
  has_media: boolean
  has_followup: boolean
}

export interface ReviewListResponse {
  results: Review[]
  total: number
  page?: number
  page_size?: number
}

export interface ReviewSummaryTopic {
  key: string
  title: string
  description: string
  mentioned_count: number
  mentioned_percent: number
}

export interface ReviewSummaryResponse {
  review_count: number
  average_rating: number
  rating_distribution: Record<string, number>
  summary_text: string
  topics: ReviewSummaryTopic[]
  highlights: string[]
}

// Legacy compatibility fields used by older review components.
export interface ReviewMedia {
  id: number
  type: 'image' | 'video'
  url: string
}

export interface ReviewHelpfulResponse {
  count: number
  liked_by_me: boolean
}
