// src/api/frontend/product.ts
import type { Product } from '@/types/frontend/product'
import { frontendRequest } from '@/utils/request'

export const frontendProductApi = {
  list: (params?: { q?: string; limit?: number }) =>
    frontendRequest.get<Product[]>('/products/', { params }),
  detail: (id: number) => frontendRequest.get<Product>(`/products/${id}/`),
}
