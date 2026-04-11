<!-- 发票模块 -->
<!-- src/components/orders/InvoiceCard.vue -->
<template>
  <section class="card invoice-card">
    <h3>Invoice Info</h3>

    <!-- 已开票 -->
    <div
      v-if="order.invoice"
      class="rows"
    >
      <div class="row">
        <span>Invoice Type</span>
        <span>{{ order.invoice.type }}</span>
      </div>

      <div class="row">
        <span>Invoice Title</span>
        <span>{{ order.invoice.title }}</span>
      </div>

      <div class="row">
        <span>Invoice Status</span>
        <span class="issued">Issued</span>
      </div>
    </div>

    <!-- 未开票占位 -->
    <div
      v-else
      class="placeholder"
    >
      <div class="title">No invoice issued</div>
      <div class="desc">
        If you need an invoice, please contact the merchant or request one
        after the order is completed.
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
  defineProps<{
    order: any
  }>()
</script>

<style scoped>
  .invoice-card {
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

  .issued {
    color: #52c41a;
    font-weight: 500;
  }

  .placeholder {
    background: #fafafa;
    border: 1px dashed #ddd;
    border-radius: 8px;
    padding: 14px;
  }

  .title {
    font-weight: 500;
    margin-bottom: 4px;
  }

  .desc {
    color: #888;
    font-size: 12px;
  }
</style>
