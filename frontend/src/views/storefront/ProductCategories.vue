<!-- src/views/storefront/ProductCategories.vue -->
<!-- 产品分类页面 -->
<template>
  <div class="Category">
    <!-- ============ 分类介绍 ============ -->
    <div class="Category-Introduction">
      <!-- 面包屑 -->
      <Breadcrumb
        :items="[
          { label: 'Home', clickable: true },
          { label: currentCategory },
        ]"
        @item-click="handleClick"
      />
      <!-- 分类标题 -->
      <h1>{{ currentCategory }}</h1>
      <div>Category Description...</div>
    </div>

    <!-- ============ 价格与排序栏 ============ -->
    <div class="price-navigation">
      <div>Availability &rarr;</div>
      <div>Price &rarr;</div>
      <div>Showing {{ totalProducts }} of {{ totalProducts }} products</div>
      <div>Best selling &rarr;</div>
    </div>

    <!-- ============ 产品网格 ============ -->
    <div class="product-display">
      <!-- 按分类渲染产品卡片 -->
      <ProductCard
        v-for="item in filteredProducts"
        :key="item.id"
        :product-data="item"
        :current-image="getPrimaryImage(item)"
        @product-click="openProduct"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  /* ================== Vue 与 Router ================== */
  import { computed, onMounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import NavBar from '@/components/NavBar.vue'
  import ProductCard from '@/components/ProductCard.vue'

  import { getPrimaryImage } from '@/utils/images'

  import { fetchCategoryProducts } from '@/services'
  import type { CategoryProducts, Product } from '@/types'

  /* ================== 路由 ================== */
  const route = useRoute()
  const router = useRouter()

  /* ================== 状态 ================== */
  const currentCategory = ref<string>('')
  const currentKeyword = ref<string>('')

  // 后台返回的分类产品映射
  const categoryProductsMap = ref<CategoryProducts>({})

  /* ================== 导航 ================== */
  const handleClick = (index: number) => {
    if (index === 0) {
      router.push({ name: 'home' })
    }
  }

  /* ================== 计算属性 ================== */
  // 当前分类下的产品
  const filteredProducts = computed<Product[]>(() => {
    const allProducts = Object.values(categoryProductsMap.value).flat()
    const q = currentKeyword.value.trim().toLowerCase()

    if (q) {
      return allProducts.filter((product) => {
        const categoryName = product.category?.name || ''
        return (
          product.name?.toLowerCase().includes(q) ||
          categoryName.toLowerCase().includes(q) ||
          product.description?.toLowerCase().includes(q) ||
          product.specifications?.toLowerCase().includes(q)
        )
      })
    }

    if (!currentCategory.value) return []
    return categoryProductsMap.value[currentCategory.value] || []
  })

  // 当前分类产品总数
  const totalProducts = computed<number>(() => {
    return filteredProducts.value.length
  })

  /* ================== 操作 ================== */
  const openProduct = (item: Product): void => {
    router.push({
      name: 'product-detail',
      params: {
        category: item.category?.name || currentCategory.value || 'all',
        id: item.id.toString(),
      },
    })
  }

  /* ================== 数据加载 ================== */
  async function updateCategory(): Promise<void> {
    const queryCategory = (route.query.category as string) || 'All Products'
    const queryKeyword = (route.query.q as string) || ''

    currentKeyword.value = queryKeyword
    currentCategory.value = queryKeyword
      ? `Search Results: "${queryKeyword}"`
      : queryCategory

    if (Object.keys(categoryProductsMap.value).length === 0) {
      try {
        categoryProductsMap.value = await fetchCategoryProducts()
      } catch (err) {
        categoryProductsMap.value = {}
      }
    }
  }

  /* ================== 生命周期 ================== */
  onMounted(updateCategory)

  watch(
    () => [route.query.category, route.query.q],
    updateCategory
  )
</script>

<style scoped>
  /* ==================== 分类介绍 ==================== */
  /* 分类介绍容器 */
  .Category-Introduction {
    background-color: #eee9e9;
    height: 400px;
    padding: 0 50px;
  }

  .Category-Introduction h1 {
    margin-top: 0;
    font-size: 3.5rem;
    font-weight: 500;
  }

  /* 面包屑容器 */
  .introduction-container {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    opacity: 0.7;
    /* 0 完全透明，1 完全不透明 */
    font-size: 0.8rem;
    padding-top: 50px;
  }

  /* 面包屑链接 */
  .nav-link {
    position: relative;
    cursor: pointer;
    padding-bottom: 3px;
    transition: color 0.3s;
  }

  /* 下划线动画 */
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

  .nav-link:hover {
    color: #007bff;
  }

  .nav-link:hover::after {
    transform: scaleX(0);
    transform-origin: right center;
  }

  /* 分隔线 */
  .separator {
    width: 1.6rem;
    height: 0.05rem;
    background-color: #333;
    margin: 0.2rem;
  }

  /* ==================== 价格导航 ==================== */
  .price-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 2rem;
  }

  /* ==================== 产品展示 ==================== */
  .product-display {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
    padding: 1rem 0;
  }

  .product-item {
    border-radius: 8px;
    background-color: #eee9e9;
  }

  .product-image-container {
    width: 100%;
    aspect-ratio: 1 / 1;
    overflow: hidden;
  }

  .product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.5s ease;
  }

  .product-item:hover .product-image {
    transform: scale(1.2);
  }

  .text-container {
    padding: 10px 10px;
  }

  .text-container p {
    margin: 0 0 0.5em 0;
  }

  .product-name {
    font-weight: 600;
    color: #333;
    cursor: pointer;
  }

  .product-reviews {
    color: #666;
    font-size: 0.9rem;
  }

  .product-price {
    font-weight: bold;
    color: #2c5aa0;
    font-size: 1.1rem;
  }

  /* ==================== 响应式 ==================== */
  @media (max-width: 1024px) {
    .product-display {
      grid-template-columns: repeat(3, 1fr);
      gap: 1.5rem;
    }
  }

  @media (max-width: 768px) {
    .Category {
      margin: 0;
    }

    .Category-Introduction {
      padding: 0 20px;
    }

    .Category-Introduction h1 {
      font-size: 1.8rem;
      line-height: 1.2;
    }

    .product-display {
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
    }

    .price-navigation {
      flex-direction: column;
      gap: 0.5rem;
      align-items: flex-start;
    }
  }

  @media (max-width: 480px) {
    .product-display {
      grid-template-columns: 1fr;
    }
  }
</style>
