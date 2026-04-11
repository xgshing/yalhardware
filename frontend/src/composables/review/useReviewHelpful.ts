import type { Review } from '@/types'

export function useReviewHelpful() {
  // Helpful API is not implemented in current backend. Keep a no-op handler
  // so older components continue to compile without runtime errors.
  const toggleHelpful = async (_review: Review) => Promise.resolve()

  return {
    toggleHelpful,
  }
}
