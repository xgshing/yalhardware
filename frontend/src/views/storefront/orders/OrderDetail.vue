<!-- src/views/storefront/orders/OrderDetail.vue -->
<template>
  <div class="orders-page">
    <div class="orders-container">
      <div v-if="orderLoaded">
        <div class="page-header">
          <div class="header-left">
            <router-link
              to="/orders"
              class="back-link"
            >
              ← Back to orders
            </router-link>

            <h1>Order Detail</h1>
            <div class="order-no">Order No: {{ order.order_no }}</div>
            <div class="order-status-text">
              Current status: {{ currentStatusLabel }}
            </div>
          </div>
        </div>

        <OrderStatusTimeline :order="order" />

        <div class="layout">
          <div class="main">
            <section class="card">
              <h2>Items</h2>
              <OrderReview :orderItems="order.items" />
            </section>

            <LogisticsCard
              v-if="showLogistics"
              :order="order"
            />

            <section class="card mobile-only">
              <h3>Order Actions</h3>
              <OrderActionsBar
                v-if="order.items"
                :order="order"
                @updated="load"
              />
            </section>

            <OrderAmountSummary :order="order" />

            <PaymentMethodCard
              v-if="showPostPayInfo"
              :order="order"
            />

            <InvoiceCard
              v-if="showPostPayInfo"
              :order="order"
            />

            <section class="card">
              <h2>Order History</h2>
              <div class="timeline">
                <div
                  v-for="step in completedSteps"
                  :key="step.key"
                  class="time-item"
                >
                  <span>{{ step.label }}</span>
                  <span>{{ formatTime(order[step.timeKey]) }}</span>
                </div>
              </div>
            </section>

            <section class="card mobile-only">
              <h3>Shipping Info</h3>
              <div class="address">
                <div>{{ order.receiver_name || '-' }}</div>
                <div>{{ order.receiver_phone || '-' }}</div>
                <div>{{ order.receiver_address || '-' }}</div>
              </div>
            </section>
          </div>

          <aside class="sidebar">
            <section class="card desktop-only">
              <h3>Order Actions</h3>
              <OrderActionsBar
                v-if="order.items"
                :order="order"
                @updated="load"
              />
            </section>

            <section class="card desktop-only">
              <h3>Shipping Info</h3>
              <div class="address">
                <div>{{ order.receiver_name || '-' }}</div>
                <div>{{ order.receiver_phone || '-' }}</div>
                <div>{{ order.receiver_address || '-' }}</div>
              </div>
            </section>
          </aside>
        </div>
      </div>

      <div
        v-else
        class="loading-placeholder"
      >
        Loading...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import InvoiceCard from '@/components/orders/InvoiceCard.vue'
  import LogisticsCard from '@/components/orders/LogisticsCard.vue'
  import OrderActionsBar from '@/components/orders/OrderActionsBar.vue'
  import OrderAmountSummary from '@/components/orders/OrderAmountSummary.vue'
  import OrderStatusTimeline from '@/components/orders/OrderStatusTimeline.vue'
  import PaymentMethodCard from '@/components/orders/PaymentMethodCard.vue'
  import OrderReview from '@/components/review/OrderReview.vue'
  import { ORDER_FLOW } from '@/constants/orderStatus'
  import { orderService } from '@/services/frontend/order'
  import { computed, onMounted, ref } from 'vue'
  import { useRoute } from 'vue-router'

  const route = useRoute()
  const order = ref<any>({})
  const orderLoaded = ref(false)

  const currentStatusLabel = computed(
    () =>
      ORDER_FLOW.find((step) => step.key === order.value.status)?.label || '-'
  )

  const completedSteps = computed(() =>
    ORDER_FLOW.filter(
      (step) =>
        order.value[step.timeKey] &&
        ORDER_FLOW.findIndex((item) => item.key === step.key) <=
          ORDER_FLOW.findIndex((item) => item.key === order.value.status)
    )
  )

  const showLogistics = computed(() =>
    ['SHIPPED', 'COMPLETED'].includes(order.value.status)
  )

  const showPostPayInfo = computed(() =>
    ['PAID', 'SHIPPED', 'COMPLETED'].includes(order.value.status)
  )

  function formatTime(time?: string) {
    return time ? new Date(time).toLocaleString() : '-'
  }

  const load = async () => {
    order.value = await orderService.fetchDetail(String(route.params.id))
    orderLoaded.value = true
  }

  onMounted(load)
</script>

<style src="@/styles/frontend/orders.css" />

<style scoped>
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .header-left {
    display: flex;
    flex-direction: column;
  }

  .back-link {
    font-size: 14px;
    color: #6b7280;
    text-decoration: none;
    cursor: pointer;
  }

  .back-link:hover {
    color: #111827;
    text-decoration: underline;
  }

  .order-no {
    font-size: 16px;
    color: #666;
  }

  .order-status-text {
    font-size: 16px;
    margin: 16px 0;
    font-weight: 700;
  }

  .layout {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
  }

  .card {
    background: #fff;
    border-radius: 12px;
    margin-bottom: 16px;
    padding: 16px;
  }

  h2,
  h3 {
    font-size: 20px;
    padding: 0 0 10px ;
    margin: 0;
  }

  .timeline {
    font-size: 13px;
    color: #555;
  }

  .time-item {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
  }

  .address {
    font-size: 14px;
    line-height: 1.6;
  }

  .loading-placeholder {
    text-align: center;
    padding: 50px 0;
    color: #999;
  }

  .mobile-only {
    display: none;
  }

  @media (max-width: 768px) {
    .layout {
      grid-template-columns: 1fr;
      gap: 0;
    }

    .desktop-only {
      display: none;
    }

    .mobile-only {
      display: block;
    }

    .back-link,
    .order-no,
    .order-status-text {
      font-size: 14px;
    }
  }
</style>
