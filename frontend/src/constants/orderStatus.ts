// src/constants/orderStatus.ts
export const ORDER_FLOW = [
  { key: 'PENDING', label: 'Pending Payment', timeKey: 'created_at' },
  { key: 'PAID', label: 'Paid', timeKey: 'paid_at' },
  { key: 'SHIPPED', label: 'Shipped', timeKey: 'shipped_at' },
  { key: 'COMPLETED', label: 'Completed', timeKey: 'completed_at' },
]
