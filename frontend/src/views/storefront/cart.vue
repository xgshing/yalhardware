<!-- src/views/storefront/cart.vue -->
<template>
  <div class="body">
    <!-- ================= 导航 ================= -->
    <Breadcrumb
      :items="[{ label: 'Home', clickable: true }, { label: purpose }]"
      @item-click="handleClick"
    />

    <div class="title">
      <h1>Shopping Cart</h1>
      <div>Continue shopping</div>
    </div>

    <div class="cart-style">
      <p>Product</p>
      <p>Price</p>
      <p>Quantity</p>
      <p>Total</p>
    </div>

    <div class="cart-header">
      <el-checkbox v-model="cartStore.isAllchecked"> select All </el-checkbox>
    </div>

    <div
      v-for="(item, index) in cartStore.items"
      :key="item.variant_id"
      class="cart-item"
    >
      <el-checkbox
        :model-value="item.checked"
        @change="() => cartStore.toggleChecked(index)"
      />

      <div class="pic-product-info">
        <!-- 商品图片 -->
        <img
          :src="item.image"
          :alt="item.name"
          class="item-img"
        />
        <div class="item-info">
          <h3>{{ item.name }}</h3>
          <p class="case-type">Case Type: {{ item.caseType }}</p>
        </div>
      </div>
      <p class="price unit-price">${{ item.price }}</p>

      <div class="quantity-cell">
        <span class="quantity-label">Quantity</span>
        <div class="cart-quantity-selector">
          <button
            class="cart-quantity-btn"
            @click="cartStore.updateQuantity(index, 'decrease')"
          >
            -
          </button>
          <input
            class="cart-quantity-input"
            :value="item.quantity"
            readonly
          />
          <button
            class="cart-quantity-btn"
            @click="cartStore.updateQuantity(index, 'increase')"
          >
            +
          </button>
        </div>
      </div>

      <div class="price line-total">${{ cartStore.calculateItemTotal(item) }}</div>

      <button
        class="remove-btn"
        @click="cartStore.removeItem(index)"
      >
        <span class="closeBtn-icon">✕</span>
        <span class="remove"> REMOVE</span>
      </button>
    </div>

    <!-- ================= 运费保险 ================= -->
    <ShippingProtection class="shipping-protection" />
  </div>

  <div class="subtotal-pay">
    <div>
      <p class="subtotal">Subtotal: ${{ cartStore.subtotal }}</p>
      <p class="tax-note">
        Taxes and
        <a
          class="policy-link"
          href="/shipping-policy"
        >
          shipping
        </a>
        calculated at checkout
      </p>
    </div>

    <el-button
      class="order check-out"
      :disabled="cartStore.checkedItems.length === 0"
      @click="checkout"
    >
      <span class="checkout-inner">
        <span>Check Out</span>
        <Icon icon="fluent-mdl2:payment-card" />
      </span>
    </el-button>
  </div>
</template>

<script setup lang="ts">
  import { useCartStore } from '@/stores/cart'
  import { computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { orderService } from '@/services'
  import { Icon } from '@iconify/vue'
  import axios from 'axios'
  import { ElMessage } from 'element-plus'

  const route = useRoute()
  const router = useRouter()
  const BYPASS_USER_AUTH = import.meta.env.VITE_BYPASS_USER_AUTH === 'true'

  // ========== 获取 Pinia 存储（Store）实例 ==========
  const cartStore = useCartStore()

  /* ================== Purpose 计算属性 ================== */
  const purpose = computed(() => {
    // 获取 query 参数
    const purposeValue = route.query.purpose as string

    // 返回处理后的值
    return purposeValue || '默认页面'
  })

  /* ================== 导航 ================== */
  const handleClick = (index: number) => {
    if (index === 0) {
      router.push({ name: 'home' })
    }
  }

  const checkout = async () => {
    try {
      if (BYPASS_USER_AUTH) {
        ElMessage.info('当前为网站免登录测试模式')
      }
      // 构建订单payload
      const payload = cartStore.buildOrderPayload()

      if (!payload.items || payload.items.length === 0) {
        ElMessage.warning('Please select items to checkout')
        return
      }

      // 调用后端创建订单
      const order = await orderService.submit(payload)
      ElMessage.success('Order created successfully')

      // 成功后跳转到确认面（带id)
      router.push({
        name: 'order-pay',
        params: {
          id: order.id,
        },
      })
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        ElMessage.error(err.response?.data?.detail || 'Failed to create order')
      } else {
        ElMessage.error('Unexpected error occurred')
      }
    }
  }
</script>

<style scoped>
  /* 页面主容器样式 */
  .body {
    min-height: 100vh;
  }

  .title {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: #999;
  }
  .title h1 {
    font-size: 3.5rem;
    font-weight: 500;
    color: #111;
  }

  .cart-style {
    display: grid;
    grid-template-columns: 32px minmax(260px, 1fr) 110px 140px 110px 120px;
    align-items: center;
    background-color: #f7f3f3;
    padding: 12px 20px;
    column-gap: 16px;
    font-size: 0.9rem;
    color: #666;
  }

  .cart-style p {
    margin: 0;
  }

  .cart-style p:first-child {
    grid-column: 2;
  }

  .cart-style p:not(:first-child) {
    justify-self: center;
  }
  .cart-item {
    display: grid;
    grid-template-columns: 32px minmax(260px, 1fr) 110px 140px 110px 120px;
    align-items: center;
    column-gap: 16px;
    padding: 15px 0;
    border-bottom: 1px solid #ddd;
  }

  .pic-product-info {
    display: flex;
    flex-direction: row;
    align-items: center;
    min-width: 0;
  }
  .item-img {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    margin-right: 16px;
    flex-shrink: 0;
  }

  .item-info {
    font-size: 0.8rem;
    min-width: 0;
  }

  .item-info h3 {
    margin: 0 0 6px;
    font-size: 1rem;
    line-height: 1.35;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .case-type {
    color: #999;
    margin: 0;
  }

  .price {
    margin: 0;
  }

  .unit-price,
  .line-total {
    justify-self: center;
    text-align: center;
  }

  .quantity-cell {
    justify-self: center;
    display: flex;
    align-items: center;
  }

  .quantity-label {
    display: none;
  }

  .cart-quantity-selector {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    min-width: 170px;
    gap: 6px;
    background-color: #fff;
    padding: 6px;
    border: 1px solid #d8d8d8;
    border-radius: 4px;
  }

  .cart-quantity-btn {
    width: 34px;
    height: 34px;
    flex: 0 0 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    border: none;
    background: #fff;
    cursor: pointer;
  }
  .cart-quantity-input {
    width: 64px;
    min-width: 0;
    height: auto;
    text-align: center;
    border: none;
    outline: none;
    font-size: 14px;
    background: #fff;
  }

  .remove-btn {
    border: none;
    background: transparent;
    padding: 0;
    margin: 0;
    font-size: 12px;
    color: #666;
    cursor: pointer;
    justify-self: end;
  }

  .shipping-protection {
    display: flex;
    justify-content: center;
  }

  .subtotal-pay {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    background-color: #f7f3f3;
    gap: 5rem;
    padding: 2.5rem 1.25rem;
  }

  .subtotal {
    font-size: 1rem;
    font-weight: 600;
  }
  .tax-note {
    font-size: 12px;
    color: #666;
  }

  .policy-link {
    color: inherit;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 3px;
    cursor: pointer;
  }

  .policy-link:hover {
    color: #333;
  }

  .order {
    width: 100%;
    padding: 0 30px;
    height: 60px;
    font-size: 15px;
    font-weight: bold;
    border-radius: 5px;
  }

  .check-out:deep(> span) {
    width: 100%;
    display: block;
  }
  .check-out {
    background-color: #333;
    width: 15rem;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .checkout-inner {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .check-out:hover {
    background-color: black;
  }
  @media (max-width: 768px) {
    .title {
      align-items: flex-end;
      gap: 8px;
      margin-bottom: 12px;
    }

    .title h1 {
      font-size: 2rem;
      margin: 0;
    }

    .cart-style {
      display: none;
    }

    .cart-header {
      padding: 10px 0;
      border-bottom: 1px solid #ddd;
      margin-bottom: 10px;
    }

    .cart-item {
      grid-template-columns: 24px 1fr;
      column-gap: 12px;
      row-gap: 10px;
      padding: 14px 0;
    }

    .cart-item > :first-child {
      grid-column: 1;
      grid-row: 1;
      align-self: start;
      margin-top: 4px;
    }

    .pic-product-info {
      grid-column: 2;
      grid-row: 1;
    }

    .item-img {
      width: 72px;
      height: 72px;
      margin-right: 12px;
    }

    .unit-price,
    .quantity-cell,
    .cart-quantity-selector,
    .line-total,
    .remove-btn {
      grid-column: 2;
      width: 100%;
    }

    .unit-price,
    .line-total {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.95rem;
    }

    .unit-price::before {
      content: 'Price';
      color: #666;
    }

    .line-total::before {
      content: 'Total';
      color: #666;
    }

    .quantity-cell {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
    }

    .quantity-label {
      display: inline-block;
      color: #666;
      font-size: 0.95rem;
    }

    .cart-quantity-selector {
      justify-content: center;
      width: auto;
      max-width: none;
      min-width: 0;
      padding: 3px;
      gap: 3px;
      margin-left: auto;
    }

    .cart-quantity-btn {
      width: 24px;
      height: 24px;
      flex: 0 0 24px;
      font-size: 14px;
    }

    .cart-quantity-input {
      width: 40px;
      flex: 0 0 40px;
      min-width: 0;
      font-size: 12px;
    }

    .remove-btn {
      justify-self: start;
      margin-top: 2px;
    }

    .subtotal-pay {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
      padding: 1rem;
    }

    .check-out {
      width: 100%;
    }
  }
</style>
