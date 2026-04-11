<!-- 物流区模块 -->
<!-- src/components/orders/LogisticsCard.vue -->
<template>
  <section class="card logistics-card">
    <h3 class="card-title">Logistics Info</h3>

    <template v-if="isShipped">
      <div
        v-for="(f, idx) in order.fulfillments"
        :key="f.id"
        class="logistics shipped"
      >
        <div class="row">
          <span class="label">Shipping Status</span>
          <span class="value shipped">{{ f.status_label || 'Shipped' }}</span>
        </div>

        <div class="row">
          <span class="label">Carrier</span>
          <span class="value">{{ f.carrier || '-' }}</span>
        </div>

        <div class="row">
          <span class="label">Tracking No.</span>
          <span class="value mono">{{ f.tracking_no || '-' }}</span>
        </div>

        <div class="row">
          <span class="label">Shipped At</span>
          <span class="value">{{ formatTime(f.shipped_at) }}</span>
        </div>

        <div class="row">
          <span class="label">Handled By</span>
          <span class="value">{{ f.operator_name || '-' }}</span>
        </div>

        <button
          v-if="f.tracking_no"
          class="btn secondary"
          @click="viewTracking(f.tracking_no)"
        >
          Track package
        </button>

        <hr v-if="(idx as number) < order.fulfillments.length - 1" />
      </div>
    </template>

    <div
      v-else
      class="logistics pending"
    >
      <div class="placeholder">
        <div class="icon">📦</div>
        <div class="text">
          <div class="title">Your order has not been shipped yet</div>
          <div class="desc">
            The order has been paid and is expected to ship within 1-3
            business days.
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  const props = defineProps<{ order: any }>()

  const isShipped = computed(() => props.order.fulfillments?.length > 0)

  function formatTime(time?: string) {
    return time ? new Date(time).toLocaleString() : '-'
  }

  function viewTracking(trackingNo?: string) {
    if (!trackingNo) return
    window.open(`https://www.kuaidi100.com/chaxun?nu=${trackingNo}`, '_blank')
  }
</script>

<style scoped>
  .logistics-card {
    padding: 16px;
  }

  .card-title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 12px;
  }

  .logistics {
    font-size: 13px;
  }

  /* 行 */
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

  .value.shipped {
    color: #52c41a;
    font-weight: 500;
  }

  .mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }

  /* 已发货按钮 */
  .btn {
    margin-top: 12px;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
  }

  .secondary {
    background: #fff;
    border: 1px solid #ddd;
    color: #333;
  }

  .secondary:hover {
    border-color: #bbb;
  }

  /* 未发货占位（Stripe 风） */
  .pending .placeholder {
    display: flex;
    gap: 12px;
    background: #fafafa;
    border: 1px dashed #ddd;
    border-radius: 8px;
    padding: 16px;
  }

  .icon {
    font-size: 28px;
    line-height: 1;
  }

  .text .title {
    font-weight: 500;
    margin-bottom: 4px;
  }

  .text .desc {
    color: #888;
    font-size: 12px;
  }
</style>
