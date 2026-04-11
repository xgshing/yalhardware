<!-- 金额明细模块 -->
<!-- src/components/orders/OrderAmountSummary.vue -->
<template>
  <section class="card amount-card">
    <h3 class="card-title">Amount Summary</h3>

    <div class="rows">
      <div class="row">
        <span>Subtotal</span>
        <span>{{ currency(subtotal) }}</span>
      </div>

      <div
        v-if="shippingFee > 0"
        class="row"
      >
        <span>Shipping</span>
        <span>{{ currency(shippingFee) }}</span>
      </div>

      <div
        v-if="discount > 0"
        class="row discount"
      >
        <span>Discount</span>
        <span>-{{ currency(discount) }}</span>
      </div>

      <div class="divider" />

      <div class="row total">
        <span>Total Paid</span>
        <span>{{ currency(total) }}</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
  const props = defineProps<{
    order: any
  }>()

  const subtotal = props.order.subtotal_amount ?? props.order.total_amount
  const shippingFee = props.order.shipping_fee ?? 0
  const discount = props.order.discount_amount ?? 0
  const total = props.order.total_amount

  function currency(value: number) {
    return `$${Number(value).toFixed(2)}`
  }
</script>

<style scoped>
  .amount-card {
    padding: 16px;
  }

  .rows {
    font-size: 13px;
  }

  .row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .discount {
    color: #52c41a;
  }

  .divider {
    height: 1px;
    background: #eee;
    margin: 10px 0;
  }

  .total {
    font-size: 14px;
    font-weight: 600;
  }
  h2,
  h3 {
    font-size: 20px;
    padding: 0 0 10px ;
    margin: 0;
  }
</style>
