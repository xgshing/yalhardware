
<template>
  <div class="product-container">
    <!-- 面包屑导航 -->
    <Breadcrumb
      :items="[
        { label: 'Home', clickable: true },
        { label: category, clickable: true },
        { label: productName },
      ]"
      @item-click="handleBreadcrumbClick"
    />

    <!-- 产品主内容区：左侧图库，右侧信息与购买操作 -->
    <div class="product-details">
      <!-- 产品图库：主图轮播 + 缩略图 -->
      <div class="product-gallery">
        <div class="main-swiper-shell">
          <Swiper
            :modules="modules"
            :navigation="true"
            :pagination="{ clickable: true }"
            effect="fade"
            class="main-swiper"
            @swiper="onMainSwiper"
            @slide-change="handleSlideChange"
          >
            <SwiperSlide
              v-for="(img, i) in images"
              :key="i"
            >
              <img
                :src="img"
                class="main-image"
                loading="lazy"
                @click="openLightbox"
              />
            </SwiperSlide>
          </Swiper>

        </div>

        <Swiper
          :modules="[FreeMode]"
          :slides-per-view="5"
          :space-between="12"
          free-mode
          watch-slides-progress
          class="thumbnail-swiper"
          @swiper="onThumbSwiper"
        >
          <SwiperSlide
            v-for="(img, i) in images"
            :key="i"
            @click="syncToIndex(i)"
          >
            <div
              class="thumbnail-container"
              :class="{ active: activeIndex === i }"
            >
              <img
                :src="img"
                class="thumbnail-image"
                loading="lazy"
              />
            </div>
          </SwiperSlide>
        </Swiper>
      </div>

      <!-- 大图预览 -->
      <vue-easy-lightbox
        :visible="lightboxVisible"
        :imgs="images"
        :index="activeIndex"
        @hide="lightboxVisible = false"
      />

      <!-- 产品信息与购买区域 -->
      <div class="product-info">
        <h1>{{ productName }}</h1>
        <p class="price">${{ productData?.price }} USD</p>
        <p class="shipping">Shipping calculated at checkout.</p>


        <!-- 规格与数量选择 -->
        <div class="product-choose-container">
          <!-- 颜色 / 款式选择 -->
          <div class="case-type">
            <div class="type-title">Case Color:</div>

            <div
              v-for="(v, i) in productData?.variants || []"
              :key="v.id"
              class="case-chip"
              :class="{ selected: selectedCaseIndex === i }"
              @click="handleSelectCase(i)"
            >
              {{ v.style_name }}
            </div>
          </div>

          <!-- 购买数量 -->
          <div class="order-row">
            <div class="quantity-title">Quantity:</div>
            <div class="quantity">
              <button @click="quantity > 1 && quantity--">-</button>

              <input
                type="number"
                v-model.number="quantity"
                min="1"
              />
              <button @click="quantity++">+</button>
            </div>
          </div>
        </div>

        <!-- 购买操作 -->
        <div class="actions">
          <button
            class="add-to-cart"
            @click="handleAddToCart"
          >
            Add to Cart
          </button>
          <button
            class="buy-now"
            @click="handleBuyNow"
          >
            Buy it now
          </button>
        </div>

        <!-- 折叠信息区 -->
        <ul class="accordion">
          <li
            v-for="(item, i) in accordionItems"
            :key="i"
            class="accordion-container"
          >
            <!-- 折叠标题 -->
            <div
              class="accordion-item"
              @click="toggleAccordion(i)"
            >
              <p class="item-title">{{ item.title }}</p>
              <span>{{ item.isOpen ? '-' : '+' }}</span>
            </div>
            <div
              v-show="item.isOpen"
              class="accordion-body"
            >
              {{ getAccordionContent(item) }}
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- 评论区 -->
    <ProductReviews
      v-if="productData && productData.id"
      :product-id="productData.id"
    />

    <!-- 相似产品推荐 -->
    <SimilarProducts
      :products="similarProducts"
      title="You May Also Like"
      subtitle="Featured Items"
      @product-click="handleProductClick"
    />
  </div>
</template>

<script setup lang="ts">
  // Vue 与路由
  import { onMounted, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import axios from 'axios'

  // 组件
  import NavBar from '@/components/NavBar.vue'
  import SimilarProducts from '@/components/SimilarProducts.vue'
  import VueEasyLightbox from 'vue-easy-lightbox'

  // Swiper
  import 'swiper/css'
  import 'swiper/css/free-mode'
  import 'swiper/css/navigation'
  import 'swiper/css/pagination'
  import { FreeMode, Navigation, Pagination } from 'swiper/modules'
  import { Swiper, SwiperSlide } from 'swiper/vue'

  // 组合式逻辑
  import { useAccordion } from '@/composables/product/useAccordion'
  import { useProduct } from '@/composables/product/useProduct'
  import { useProductCart } from '@/composables/product/useProductCart'
  import { useProductGallery } from '@/composables/product/useProductGallery'
  import { useProductVariants } from '@/composables/product/useProductVariants'
  import { useUserStore } from '@/stores/user'
  import { ElMessage } from 'element-plus'

  // API
  import { fetchCategoryProducts, orderService } from '@/services'

  // 基础实例
  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()
  const BYPASS_USER_AUTH = import.meta.env.VITE_BYPASS_USER_AUTH === 'true'
  const modules = [Navigation, Pagination]

  // 产品基础数据
  const {
    productData,
    images,
    productName,
    category,
    similarProducts,
    categoryProductsMap,
  } = useProduct()

  // 图片轮播与灯箱
  const {
    mainSwiper,
    activeIndex,
    lightboxVisible,
    onMainSwiper,
    onThumbSwiper,
    openLightbox,
    syncToIndex,
  } = useProductGallery()

  // 款式选择
  const { selectedCaseIndex, selectCase, syncByImageIndex } =
    useProductVariants(() => productData.value)

  // 购物车
  const { addToCart } = useProductCart()

  // 折叠面板
  const { accordionItems, toggleAccordion, getAccordionContent } =
    useAccordion(productData)

  // 购买数量
  const quantity = ref(1)

  // 未登录时跳转到登录页
  const redirectToLogin = () => {
    router.push({
      name: 'login',
      query: { purpose: 'Login', redirect: route.fullPath },
    })
  }

  // 购买前校验登录状态
  const ensureCanOrder = () => {
    if (BYPASS_USER_AUTH) {
      ElMessage.info('当前为网站免登录测试模式')
      return true
    }

    if (!userStore.isLogin) {
      redirectToLogin()
      return false
    }

    return true
  }
  // 主图切换时，同步缩略图与款式状态
  const handleSlideChange = () => {
    const index = mainSwiper.value?.realIndex ?? 0
    syncToIndex(index)
    syncByImageIndex(index)
  }
  // 选择款式时，同步主图位置
  const handleSelectCase = (index: number) => {
    selectCase(index)
    syncToIndex(index)
  }
  // 加入购物车
  const handleAddToCart = () => {
    if (!ensureCanOrder()) return
    if (!productData.value) return
    addToCart(productData.value, quantity.value, selectedCaseIndex.value)
  }

  // 立即购买
  const handleBuyNow = async () => {
    if (!ensureCanOrder()) return
    if (!productData.value) return

    const variant = productData.value.variants?.[selectedCaseIndex.value]
    if (!variant) {
      ElMessage.warning('Please select a valid style')
      return
    }

    try {
      const order = await orderService.submit({
        items: [
          {
            variant_id: variant.id,
            quantity: quantity.value,
          },
        ],
      })

      ElMessage.success('Order created successfully')
      router.push({
        name: 'order-pay',
        params: { id: order.id },
      })
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        ElMessage.error(err.response?.data?.detail || 'Failed to create order')
      } else {
        ElMessage.error('Unexpected error occurred')
      }
    }
  }
  // 面包屑点击跳转
  const handleBreadcrumbClick = (index: number) => {
    if (index === 0) {
      router.push({ name: 'home' })
    }
    if (index === 1) {
      router.push({
        name: 'product-categories',
        query: { category: category.value },
      })
    }
  }
  // 相似产品点击跳转
  const handleProductClick = (p: any) => {
    router.push({
      name: 'product-detail',
      params: { category: category.value, id: p.id },
    })
  }
  // 页面挂载后拉取同分类商品
  onMounted(async () => {
    categoryProductsMap.value = await fetchCategoryProducts()
  })
</script>

<style scoped>
  /* 基础标题 */
  h1 {
    font-size: 1.3rem;
  }

  /* 页面主容器 */
  .product-container {
    margin: 0 auto;
  }
  /* 面包屑 */
  .breadcrumb {
    display: flex;
    gap: 8px;
    align-items: center;
    color: #666;
  }
  /* 面包屑可点击项 */
  .nav-link {
    position: relative;

    cursor: pointer;
    padding-bottom: 3px;

    transition: color 0.3s;

  }
  /* 面包屑下划线 */
  .nav-link::after {
    content: '';

    position: absolute;

    width: 100%;

    height: 1px;
    bottom: 0;
    left: 0;
    background-color: #333;
    transition: transform 0.5s ease;

    transform: scaleX(1);

    transform-origin: left center;

  }
  /* 面包屑悬浮态 */
  .nav-link:hover {
    color: #007bff;

  }
  /* 面包屑悬浮时隐藏下划线 */
  .nav-link:hover::after {
    transform: scaleX(0);

    transform-origin: right center;

  }
  /* 主内容区：左图右文 */
  .product-details {
    display: flex;
    gap: 24px;
    align-items: flex-start;
  }
  /* 左侧图库 */
  .product-gallery {
    width: 50%;
    position: relative;
  }

  /* 主图轮播外层 */
  .main-swiper-shell {
    position: relative;
  }
  /* 主图轮播 */
  .main-swiper {
    width: 100%;
    height: 600px;
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    cursor: grab;

  }
  /* 主图轮播拖拽态 */
  .main-swiper:active {
    cursor: grabbing;

  }
  /* 主图图片 */
  .main-image-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f8f8;
  }
  /* 主图图片本身 */
  .main-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: zoom-in;

  }
  /* 缩略图轮播 */
  .thumbnail-swiper {
    width: 100%;
    height: auto;
    padding: 5px 0;

  }

  /* 缩略图容器 */
  .thumbnail-container {
    width: 100%;
    aspect-ratio: 1 / 1;

    padding: 4px;
    border: 2px solid transparent;
    border-radius: 6px;
    transition: all 0.3s ease;
    cursor: pointer;
    border: 1px solid #e8e8e8;
    opacity: 0.5;

  }
  /* 缩略图悬浮态 */
  .thumbnail-container:hover {
    border-color: #bfa48f;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
    opacity: 0.8;

  }
  /* 当前选中的缩略图 */
  .thumbnail-container.active {
    border-color: #7b5a43;
    background: #fffaf7;
    opacity: 1;

  }
  /* 缩略图图片 */
  .thumbnail-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
  }

  /* 主图左右箭头 */
  :deep(.swiper-button-next),
  :deep(.swiper-button-prev) {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #333;

    background: rgba(255, 255, 255, 0.8);

    width: 40px;
    height: 40px;
    border-radius: 50%;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    --swiper-navigation-sides-offset: 16px;
  }
  /* 隐藏 Swiper 默认 svg 图标 */
  :deep(.swiper-button-next svg),
  :deep(.swiper-button-prev svg) {
    display: none !important;
  }
  /* 自定义左右箭头字符 */
  :deep(.swiper-button-prev::before),
  :deep(.swiper-button-next::before) {
    display: block;
    font-family: Arial, sans-serif;
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
    color: #7b5a43;
  }

  :deep(.swiper-button-prev::before) {
    content: '←';
  }
  :deep(.swiper-button-next::before) {
    content: '→';
  }
  /* 轮播分页点 */
  :deep(.swiper-pagination-bullet) {
    background: rgba(255, 255, 255, 0.8);
    opacity: 0.7;
  }
  /* 当前激活的分页点 */
  :deep(.swiper-pagination-bullet-active) {
    background: #ff4444;
    opacity: 1;
  }


  .thumbs {
    display: flex;
    gap: 10px;
    margin-top: 12px;
    overflow-x: auto;
    padding-bottom: 8px;
    -webkit-overflow-scrolling: touch;
  }

  /* 右侧产品信息 */
  .product-info {
    width: 50%;
    padding-top: 8px;
  }

  /* 价格 */
  .price {
    font-size: 16px;
    font-weight: 700;
    margin-top: 6px;
    margin-bottom: 8px;
  }

  /* 评论摘要 */
  .reviews {
    color: #b36a3a;
    margin-bottom: 12px;
  }
  /* 规格与数量选择区域 */
  .product-choose-container {
    background: #eee9e9;
    padding: 30px;
  }
  /* 规格列表 */
  .case-type {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 14px 0;
  }

  /* 规格标题 */
  .type-title {
    display: block;
    width: 100%;

  }
  /* 规格按钮 */
  .case-chip {
    padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid white;
    cursor: pointer;
    background-color: white;
  }
  /* 规格按钮悬浮态 */
  .case-chip:hover {
    border-color: #bfa48f;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
  }
  /* 当前选中的规格 */
  .case-chip.selected {
    border-color: #7b5a43;
    background: #fffaf7;
  }
  /* 数量选择区 */
  .order-row {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 18px;
  }
  /* 数量输入器 */
  .quantity {
    display: inline-flex;
    width: fit-content;
    min-width: 170px;
    align-items: center;
    gap: 6px;
    background-color: white;
    padding: 6px;
    border-radius: 8px;
  }
  /* 数量按钮 */
  .quantity button {
    width: 34px;
    height: 34px;
    border: none;
    background: white;
    cursor: pointer;
    font-size: 18px;
    border-radius: 6px;
  }
  /* 数量输入框 */
  .quantity input {
    width: 64px;
    text-align: center;
    border: none;
    outline: none;
    font-size: 14px;
    appearance: textfield;
    -moz-appearance: textfield;
  }

  .quantity input::-webkit-outer-spin-button,
  .quantity input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  /* 购买操作按钮区 */
  .actions {
    display: flex;
    margin-top: 30px;
    gap: 8px;
  }
  /* 加入购物车按钮 */
  .add-to-cart {
    width: 50%;
    border-radius: 8px;
    border: 1px solid #bfa48f;
    background: white;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  /* 加入购物车悬浮态 */
  .add-to-cart:hover {
    background: #7b5a43;
    color: white;
  }
  /* 立即购买按钮 */
  .buy-now {
    width: 50%;
    padding: 20px 0;
    border-radius: 8px;
    background: #333;
    color: white;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  /* 立即购买悬浮态 */
  .buy-now:hover {
    background-color: black;
  }
  /* 折叠区域 */
  .accordion {
    margin-top: 80px;
    padding-left: 0;
    margin-left: 0;
    list-style: none;
  }
  /* 折叠项容器 */
  .accordion-container {
    position: relative;
    overflow: hidden;

    box-shadow:
      inset 0 1px 0 #ddd,
       inset 0 -1px 0 #ddd;


  }
  /* 折叠项上下边线动画 */
  .accordion-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;

    background-color: #666;
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s ease;
    z-index: 2;
  }

  /* 折叠项上下边线动画 */
  .accordion-container::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background-color: #666;
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s ease;
    z-index: 2;
  }

  /* 折叠项悬浮时显示边线 */
  .accordion-container:hover::before,
  .accordion-container:hover::after {
    transform: scaleX(1);
  }

  /* 折叠标题栏 */
  .accordion-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
  }

  /* 折叠标题 */
  .item-title {
    font-size: 1.5rem;
  }
  /* 折叠内容 */
  .accordion-body {
    padding: 10px 30px;
    color: #666;
    line-height: 1.6;
  }
  /* 相似产品区域 */
  .about-root {
    display: flex;
    width: 100%;
    gap: 20px;
    padding: 20px;
    box-sizing: border-box;

  }
  /* 相似产品左栏 */
  .left-col {
    width: 25%;

    background: #bfa48f;
    padding: 16px;
    border-radius: 10px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
  }
  /* 相似产品右栏 */
  .right-col {
    width: 75%;

  }
  /* 相似产品 Swiper */
  .products-swiper {
    width: 100%;

    box-sizing: border-box;

  }
  /* 相似产品单项 */
  .product-slide {
    display: flex;
  }
  /* 产品卡片 */
  .product-card {
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    padding: 10px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  /* 产品卡片图片 */
  .product-card img {
    width: 100%;
    height: 280px;
    object-fit: cover;
    border-radius: 8px;
  }
  /* 卡片底部信息 */
  .pc-meta {
    padding-top: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  /* 卡片标题 */
  .pc-title {
    font-size: 14px;
    line-height: 1.2;
    flex: 1;
    margin-right: 8px;
    overflow: hidden;
    height: 2.4em;
  }
  /* 卡片价格 */
  .pc-price {
    color: #007aff;
    font-weight: 700;
  }
  /* 外部滑块控制区 */
  .controls-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 16px;
  }
  /* 外部箭头按钮 */
  .arrow-btn {
    min-width: 38px;
    height: 34px;
    background: #111;
    color: #fff;
    border: none;

    border-radius: 8px;
    cursor: pointer;
    font-size: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  /* 外部箭头禁用态 */
  .arrow-btn:disabled {
    opacity: 0.35;

    cursor: not-allowed;

  }
  /* 进度条轨道 */
  .scroll-track {
    flex: 1;

    height: 10px;
    background: rgba(0, 0, 0, 0.06);
    border-radius: 999px;

    position: relative;

    overflow: hidden;

  }
  /* 进度条滑块 */
  .scroll-thumb {
    position: absolute;

    left: 0;

    top: 0;

    height: 100%;

    background: linear-gradient(90deg, #007aff, #00b7ff);

    border-radius: 999px;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    touch-action: none;

    cursor: grab;

    will-change: transform;

  }
  /* 滑块拖拽态 */
  .scroll-thumb:active {
    cursor: grabbing;
  }
  /* 移动端布局 */
  @media (max-width: 768px) {
    .product-details {
      display: flex;
      flex-direction: column;

    }
    .product-gallery {
      width: 100%;
    }
    .product-info{
      width: 100%;
    }

    .order-row {
      gap: 10px;
      margin-top: 14px;
    }

    .quantity {
      width: 100%;
      max-width: 220px;
      min-width: 0;
      padding: 4px;
      gap: 4px;
    }

    .quantity button {
      width: 36px;
      height: 36px;
      flex: 0 0 36px;
      font-size: 18px;
    }

    .quantity input {
      width: auto;
      min-width: 0;
      flex: 1;
      font-size: 16px;
    }

    .main-swiper {
      height: 300px;
    }
    .thumbnail-swiper {
      height: 80px;
    }
    .link-page {
      font-size: 12px;
      gap: 6px;
      flex-wrap: wrap;

    }

    .nav-link {
      padding-bottom: 2px;

    }

    .nav-link::after {
      height: 1px;

    }
  }

  :deep(.swiper-button-prev::before),
  :deep(.swiper-button-next::before) {
    font-weight: 300;
  }

</style>


