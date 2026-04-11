<!-- 订单操作区（支付/取消/确认） -->
<!-- src/components/orders/OrderActionsBar.vue -->
<template>
  <div
    v-if="validActions.length"
    class="order-actions"
  >
    <button
      v-for="action in validActions"
      :key="action"
      :class="['btn', action === primaryAction ? 'primary' : 'secondary']"
      @click="onActionClick(action)"
      :disabled="loading"
    >
      {{ actionText[action] }}
    </button>

    <!-- 二次确认弹窗 -->
    <ConfirmModal
      :visible="confirmVisible"
      :title="confirmTitle"
      :content="confirmContent"
      :confirm-text="confirmButtonText"
      :loading="loading"
      @cancel="closeConfirm"
      @confirm="handleConfirm"
    />
  </div>
</template>

<script setup lang="ts">
  import ConfirmModal from '@/components/common/ConfirmModal.vue'
  import { orderService } from '@/services/frontend/order'
  import { computed, ref } from 'vue'

  const props = defineProps<{
    order: any
  }>()

  const emit = defineEmits<{
    (e: 'updated'): void
  }>()

  const loading = ref(false)
  const confirmVisible = ref(false)
  const pendingAction = ref<string | null>(null)

  /**
   * 文案映射
   */
  const actionText: Record<string, string> = {
    pay: 'Pay now',
    cancel: 'Cancel order',
    confirm: 'Confirm delivery',
  }

  // 只允许已知 action
  const validActions = computed(() => {
    return (props.order.available_actions || []).filter(
      (action: string) => actionText[action]
    )
  })

  /**
   * 只有一个主操作（Stripe / Amazon）
   */
  const primaryAction = computed(() => {
    return validActions.value[0]
  })

  /**
   * 哪些操作需要二次确认
   */
  const needConfirm = ['cancel', 'confirm']

  function onActionClick(action: string) {
    if (needConfirm.includes(action)) {
      pendingAction.value = action
      confirmVisible.value = true
      return
    }

    executeAction(action)
  }

  function closeConfirm() {
    confirmVisible.value = false
    pendingAction.value = null
  }

  /**
   * 二次确认文案
   */
  const confirmTitle = computed(() => {
    if (pendingAction.value === 'cancel') return 'Cancel this order?'
    if (pendingAction.value === 'confirm') return 'Confirm item received?'
    return ''
  })

  const confirmContent = computed(() => {
    if (pendingAction.value === 'cancel') {
      return 'This action cannot be undone. Do you want to continue?'
    }
    if (pendingAction.value === 'confirm') {
      return 'The order will be marked as completed after confirmation.'
    }
    return ''
  })

  const confirmButtonText = computed(() => {
    if (pendingAction.value === 'cancel') return 'Cancel order'
    if (pendingAction.value === 'confirm') return 'Confirm delivery'
    return 'Confirm'
  })

  async function handleConfirm() {
    if (!pendingAction.value) return
    await executeAction(pendingAction.value)
    closeConfirm()
  }

  /**
   * 实际执行操作
   */
  async function executeAction(action: string) {
    const handlers: Record<string, () => Promise<void>> = {
      pay: () => orderService.payOrder(props.order.id),
      cancel: () => orderService.cancelOrder(props.order.id),
      confirm: () => orderService.confirmOrder(props.order.id),
    }

    const handler = handlers[action]
    if (!handler) return

    loading.value = true
    try {
      await handler()
      emit('updated')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .order-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }

  /* 通用按钮 */
  .btn {
    font-size: 13px;
    padding: 6px 14px;
    border-radius: 4px;
    cursor: pointer;
    border: 1px solid transparent;
  }

  /* 主操作（Amazon 蓝） */
  .primary {
    background-color: #409eff;
    border: 1px solid #409eff;
    color: #fff;
  }

  .primary:hover {
    background-color: #66b1ff;
    border-color: #66b1ff;
  }

  /* 次操作（弱化） */
  .secondary {
    background: #fff;
    border: 1px solid #ddd;
    color: #666;
  }

  .secondary:hover {
    border-color: #bbb;
    color: #333;
  }
</style>
