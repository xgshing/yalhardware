<!--
  拉订单列表
  控制整体布局
  -->
<!-- src/views/storefront/orders/OrderList.vue -->
<template>
  <div class="orders-page">
    <div class="orders-container">
      <OrderCard
        v-for="order in orders"
        :key="order.id"
        :order="order"
        @updated="load"
      />

      <div
        v-if="!orders.length"
        class="empty"
      >
        No orders yet.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import OrderCard from '@/components/orders/OrderCard.vue'
  import { orderService } from '@/services'
  import { onMounted, ref } from 'vue'

  const orders = ref<any[]>([])

  async function load() {
    orders.value = await orderService.fetchMyOrders()
  }

  onMounted(load)
</script>

<style src="@/styles/frontend/orders.css" />

<style scoped>
/* 空状态 */
.empty {
  text-align: center;
  color: #999;
  padding: 60px 0;
  font-size: 14px;
}
</style>
