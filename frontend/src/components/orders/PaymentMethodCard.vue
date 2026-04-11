<!-- 支付方式模块 -->
<!-- src/components/orders/PaymentMethodCard.vue -->
<template>
  <section class="card payment-card">
    <h3>Payment Method</h3>

    <div class="row">
      <span class="label">Method</span>
      <span class="value">
        {{ paymentLabel }}
      </span>
    </div>

    <div class="row">
      <span class="label">Payment Status</span>
      <span
        class="value"
        :class="statusClass"
      >
        {{ statusText }}
      </span>
    </div>

    <div
      v-if="order.paid_at"
      class="row"
    >
      <span class="label">Paid At</span>
      <span class="value">{{ formatTime(order.paid_at) }}</span>
    </div>
  </section>
</template>

<script setup lang="ts">
  import { computed } from 'vue'

  const props = defineProps<{
    order: any
  }>()

  const paymentLabel = computed(() => {
    return props.order.payment_method_label || props.order.payment_method || '-'
  })

  const statusText = computed(() => {
    if (props.order.status === 'PAID') return 'Paid'
    if (props.order.status === 'PENDING') return 'Pending Payment'
    return '-'
  })

  const statusClass = computed(() => {
    return props.order.status === 'PAID' ? 'paid' : 'pending'
  })

  function formatTime(time: string) {
    return new Date(time).toLocaleString()
  }
</script>

<style scoped>
  .payment-card {
    padding: 16px;
    font-size: 13px;
  }

  h2,
  h3 {
    font-size: 20px;
    padding: 0 0 10px ;
    margin: 0;
  }

  .row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .label {
    color: #888;
  }

  .value {
    color: #111;
  }

  .paid {
    color: #52c41a;
    font-weight: 500;
  }

  .pending {
    color: #faad14;
  }
</style>
