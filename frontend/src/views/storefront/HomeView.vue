<!-- 首页：展示主推产品、分类入口与推荐商品。 -->
<template>
  <main class="main-content">
    <section class="favorite-products">
      <h1>Favorites</h1>
      <div class="products-row">
        <div
          v-if="topProduct"
          class="product product-no_1"
        >
          <img
            :src="topProduct.cover"
            :alt="topProduct.name"
            class="main-product-image"
          />

          <!-- 销量第1的产品：悬停时切换展示图，点击进入详情页。 -->
          <div
            class="product-info"
            @click="openProduct(topProduct)"
            @mouseenter="handleProductHover(topProduct.id)"
            @mouseleave="handleProductLeave(topProduct.id)"
          >
            <div class="thumbnail-container">
              <img
                :src="getCurrentImage(topProduct)"
                :alt="topProduct.name"
                class="product-thumbnail"
              />
            </div>

            <div class="product-details">
              <div class="first-product-title">{{ topProduct.name }}</div>
              <div class="first-product-rating">
                <span class="first-product-stars">
                  <StarRating
                    :value="getProductRating(topProduct)"
                    size="13px"
                  />
                </span>
                <span class="first-product-rating-value">
                  {{ getProductRating(topProduct).toFixed(1) }}
                </span>
              </div>
              <div class="first-product-reviews">
                {{ getProductReviewsText(topProduct) }}
              </div>
              <div class="first-product-price">{{ getProductPriceText(topProduct) }}</div>
              <div class="first-product-sales">
                Purchased {{ getProductSalesVolume(topProduct) }} times
              </div>
            </div>

            <div class="circle">↗</div>
          </div>
        </div>

        <!-- 销量第2、第3的产品，复用 ProductCard，保持卡片样式一致。 -->
        <div class="product-ranking-grid">
          <ProductCard
            v-for="item in secondAndThirdProducts"
            :key="item.id"
            :product-data="item"
            :current-image="getCurrentImage(item)"
            :show-sales-volume="true"
            @product-click="openProduct"
            @mouse-enter="() => handleProductHover(item.id)"
            @mouse-leave="() => handleProductLeave(item.id)"
          />
        </div>
      </div>
    </section>

    <!-- 公司承诺 -->
    <div class="commitment-container">
      <div
        v-for="item in commitments"
        :key="item.id"
        class="commitment-item"
      >
        <p class="title">{{ item.title }}</p>
        <p class="desc">{{ item.description }}</p>
      </div>
    </div>

    <!-- 公司的追求 -->
    <h1>Beyond beauty: crafting a better future</h1>
    <div class="sustainable-craftsmanship-container">
      <SustainableCraftsmanshipCard
        class="fixed-left-card"
        :title="cardsData[0]?.title ?? ''"
        :description="cardsData[0]?.description ?? ''"
        :image-url="cardsData[0]?.imageUrl ?? ''"
        :show-number="false"
        :is-left-fixed="true"
      />

      <div class="right-container">
        <InteractiveCard
          v-for="(card, index) in rightCardsData"
          :key="card.id"
          :id="card.id"
          :title="card.title"
          :description="card.description"
          :image-url="card.imageUrl"
          :number="index + 2"
          :is-hovered="productHoverStates[card.id] || false"
          @mouseenter="handleProductHover(card.id)"
          @mouseleave="handleProductLeave(card.id)"
        />
      </div>
    </div>

    <!-- 产品分类 -->
    <h1>Product categories</h1>
    <div class="category-grid">
      <RouterLink
        v-for="(products, categoryName) in categoryList"
        :key="categoryName"
        class="category-card category-card-link"
        :to="{ name: 'product-categories', query: { category: categoryName } }"
      >
        <div class="img-container">
          <img
            :src="getCategoryImage(products)"
            :alt="categoryName"
            class="category-image"
          />
        </div>

        <div class="title-arrow">
          <p class="category-title">{{ categoryName }}</p>
          <p class="right-arrow">↗</p>
        </div>

        <p class="category-count">{{ products.length }} Items</p>
      </RouterLink>
    </div>

    <!-- 产品工艺轮播图 -->
    <Carousel
      :slides="carouselData"
      :duration="3000"
      :speed="1000"
    />

    <!-- 推荐产品 -->
    <div class="product-recommendations">
      <h1>Recommended products</h1>
      <div class="recommended-grid">
        <ProductCard
          v-for="item in recommendedProducts"
          :key="item.id"
          :product-data="item"
          :current-image="getCurrentImage(item)"
          @product-click="openProduct"
          @mouse-enter="() => handleProductHover(item.id)"
          @mouse-leave="() => handleProductLeave(item.id)"
        />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'

  import Carousel from '@/components/Carousel/Carousel.vue'
  import InteractiveCard from '@/components/CorporationMission/InteractiveCard.vue'
  import SustainableCraftsmanshipCard from '@/components/CorporationMission/SustainableCraftsmanshipCard.vue'
  import ProductCard from '@/components/ProductCard.vue'
  import StarRating from '@/components/common/StarRating.vue'
  import { useHomeData } from '@/composables/useHomeData'

  import type { Product } from '@/types'

  const router = useRouter()

  const {
    productsByCategory,
    products,
    commitments,
    cardsData,
    carouselData,
    recommendedProducts,
    load,
  } = useHomeData()

  const categoryList = computed(() => productsByCategory.value)
  const rightCardsData = computed(() => cardsData.value.slice(1))

  // 记录每个产品的悬停状态，用于切换卡片展示图。
  const productHoverStates = ref<Record<number, boolean>>({})

  const handleProductHover = (id: number) => {
    productHoverStates.value[id] = true
  }

  const handleProductLeave = (id: number) => {
    productHoverStates.value[id] = false
  }

  // 将后端返回的多种图片字段整理成前台统一使用的图片数组。
  const normalizeImages = (product: Product): string[] => {
    const base = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '')
    const images: string[] = []

    if (product.cover) {
      images.push(
        product.cover.startsWith('http')
          ? product.cover
          : `${base}${product.cover}`
      )
    }

    if (product.variants?.length) {
      product.variants.forEach((variant) => {
        if (variant.style_image) {
          images.push(
            variant.style_image.startsWith('http')
              ? variant.style_image
              : `${base}${variant.style_image}`
          )
        }
      })
    }

    if (product.detail_images?.length) {
      product.detail_images.forEach((image) => {
        if (image.image) {
          images.push(
            image.image.startsWith('http') ? image.image : `${base}${image.image}`
          )
        }
      })
    }

    if (!images.length) images.push('/default-product.png')
    return images
  }

  // 悬停时优先展示备用图，没有备用图时回退到默认顺序。
  const getCurrentImage = (product: Product): string => {
    const images = normalizeImages(product)
    const isHovered = !!productHoverStates.value[product.id]

    if (isHovered && images.length > 1) {
      return images[2] ?? images[1] ?? images[0] ?? '/default-product.png'
    }

    return images[1] ?? images[0] ?? '/default-product.png'
  }

  const getCategoryImage = (products: Product[]): string => {
    const firstImage = products
      .map((product) => normalizeImages(product)[0])
      .find((image) => !!image)

    return firstImage ?? '/default-category.png'
  }

  const allProducts = computed(() =>
    Object.values(productsByCategory.value).flatMap((group) => group)
  )

  const sortedProducts = computed(() =>
    [...allProducts.value].sort(
      (a, b) => (b.salesVolume || 0) - (a.salesVolume || 0)
    )
  )

  const topProduct = computed(() => sortedProducts.value[0])

  const secondAndThirdProducts = computed(() =>
    sortedProducts.value.slice(1, 3)
  )

  const getProductRating = (product?: Product): number => {
    const raw = Number(product?.rating ?? product?.average_rating)
    if (!Number.isFinite(raw)) return 0
    return Math.max(0, Math.min(5, raw))
  }

  const getProductReviewsText = (product?: Product): string => {
    const raw = product?.review_count ?? product?.reviews
    const count = Number(raw)
    if (Number.isFinite(count) && count >= 0) return `${count} Reviews`
    return `${raw || 0} Reviews`
  }

  const getProductPriceText = (product?: Product): string => {
    const price = product?.price

    if (typeof price === 'number' && Number.isFinite(price)) {
      return `$${price.toFixed(2)} USD`
    }

    if (price && typeof price === 'object') {
      const current = Number((price as { current?: number }).current)
      if (Number.isFinite(current)) return `$${current.toFixed(2)} USD`
    }

    return '$0.00 USD'
  }

  const getProductSalesVolume = (product?: Product): number => {
    const volume = Number(product?.salesVolume)
    return Number.isFinite(volume) && volume > 0 ? volume : 0
  }

  const findProductCategoryName = (id: number): string => {
    const product = products.value.find((item) => item.id === id)
    return product?.category?.name ?? 'Uncategorized'
  }

  const openProduct = (product: Product) => {
    const categoryName = findProductCategoryName(product.id)

    router.push({
      name: 'product-detail',
      params: { category: categoryName, id: product.id.toString() },
    })
  }

  onMounted(async () => {
    try {
      await load()
    } catch (error) {
      console.error('Failed to load home page data', error)
    }
  })
</script>

<style scoped>
  h1 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 2rem;
    font-weight: 400;
  }

  .products-row {
    display: flex;
    gap: 0.5rem;
    min-height: 500px;
    margin: 20px 0;
  }

  .product {
    display: flex;
    height: 550px;
    overflow: hidden;
    border-radius: 8px;
  }

  .product-no_1 {
    position: relative;
    width: 50%;
    min-width: 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  }

  .main-product-image {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* 主推产品信息卡悬浮在大图上方。 */
  .product-info {
    position: absolute;
    bottom: 30px;
    left: 30px;
    z-index: 10;
    display: flex;
    flex-direction: row;
    align-items: center;
    height: 120px;
    padding: 20px;
    border-radius: 5px;
    background-color: #eee9e9;
    cursor: pointer;
  }

  .thumbnail-container {
    width: 120px;
    height: 120px;
    flex: 0 0 120px;
    overflow: hidden;
    position: relative;
  }

  .product-thumbnail {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: all 0.5s ease;
  }

  .product-details {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    margin-left: 20px;
  }

  .first-product-title {
    font-size: 18px;
    font-weight: 600;
    color: #222;
  }

  .first-product-sales {
    font-size: 14px;
    color: #475569;
  }

  .first-product-rating {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .first-product-stars {
    display: inline-flex;
    gap: 2px;
  }

  .first-product-rating-value {
    font-size: 13px;
    font-weight: 600;
    color: #1e293b;
  }

  .first-product-reviews {
    font-size: 14px;
    color: #777;
  }

  .first-product-price {
    font-size: 12px;
    font-weight: 600;
    color: #111;
    margin-top: 4px;
  }

  .circle {
    width: 60px;
    height: 60px;
    flex: 0 0 60px;
    margin-left: auto;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 50%;
    border: 1px solid #333;
    font-size: 18px;
    transition: all 0.5s ease;
  }

  .product-info:hover .circle {
    background-color: #333;
    color: white;
  }

  .product-info:hover .product-thumbnail {
    transform: scale(1.2);
  }

  .product-ranking-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
    width: 100%;
  }

  .product-card-image-wrapper {
    width: 100%;
    height: 350px;
    overflow: hidden;
  }

  .product-card-image {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    object-fit: cover;
    cursor: pointer;
    transition:
      opacity 0.5s ease,
      transform 0.9s ease;
  }

  .product-card-image:hover {
    transform: scale(1.2);
  }

  .product-card-content {
    margin: 20px;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 8px;
    font-family:
      -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial,
      sans-serif;
  }

  .product-card-title {
    font-size: 16px;
    font-weight: 600;
    color: #222;
    line-height: 1.3;
  }

  .product-card-reviews {
    font-size: 14px;
    color: #777;
    margin-top: auto;
    line-height: 2;
  }

  .product-card-price {
    font-size: 16px;
    font-weight: 600;
    color: #111;
    margin-top: 4px;
  }

  .commitment-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
    padding: 0 60px;
    margin-bottom: 50px;
    border-radius: 8px;
    background-color: #eee9e9;
  }

  .title {
    font-size: 3.5rem;
    font-weight: 600;
    margin-bottom: 10px;
  }

  .desc {
    font-size: 1.5rem;
    color: #777;
    line-height: 1.6;
  }

  .sustainable-craftsmanship-container {
    display: flex;
    width: 100%;
    height: 550px;
    margin-bottom: 50px;
    gap: 20px;
  }

  .fixed-left-card {
    width: 100%;
    height: 100%;
  }

  .right-container {
    flex: 1;
    display: flex;
    gap: 20px;
    height: 100%;
  }

  .right-container > * {
    flex: 1;
  }

  .category-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
    margin-bottom: 50px;
  }

  .category-card-link {
    display: block;
    color: inherit;
    text-decoration: none;
  }

  .img-container {
    width: 100%;
    aspect-ratio: 1 / 1;
  }

  .category-image {
    width: 100%;
    height: 100%;
    cursor: pointer;
    transition:
      transform 0.5s ease,
      box-shadow 0.2s ease;
  }

  .category-image:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  }

  .title-arrow {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0 20px;
    cursor: pointer;
  }

  /* 分类标题的下划线动效，用来统一卡片的交互反馈。 */
  .title-arrow::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    height: 1px;
    width: 100%;
    background-color: #333;
    transform: scaleX(0);
    transform-origin: left center;
    transition: transform 0.3s ease;
  }

  .title-arrow:hover::after {
    transform: scaleX(1);
  }

  .category-title {
    font-weight: 600;
    margin-bottom: 0.3rem;
    font-size: 1rem;
  }

  .right-arrow {
    font-size: 1.1rem;
  }

  .category-count {
    font-size: 0.9rem;
    color: #666;
    padding: 0 20px;
    margin-top: 10px;
  }

  .product-recommendations h1 {
    margin-bottom: 20px;
    font-size: 2.6rem;
    font-weight: 400;
  }

  .recommended-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    width: 100%;
  }


  @media (max-width: 768px) {
    .products-row {
      flex-direction: column;
    }

    .product {
      height: auto !important;
    }

    .product-ranking-grid {
      grid-template-columns: 1fr;
    }

    .main-product-image {
      height: 100%;
      object-fit: cover;
    }

    .product-no_1 {
      width: 100%;
    }
    .product-info {
      left: 12px;
      right: 12px;
      bottom: 12px;
      height: auto;
      padding: 12px;
      gap: 10px;
      margin: 0;
      z-index: 12;
    }

    .commitment-container {
      grid-template-columns: 1fr;
      justify-items: center;
      text-align: center;
      padding: 16px;
      gap: 16px;
    }

    .commitment-item {
      width: 100%;
      max-width: 560px;
      margin: 0 auto;
    }

    .commitment-item .title {
      font-size: 1.8rem;
      margin-bottom: 8px;
    }

    .commitment-item .desc {
      font-size: 1rem;
      line-height: 1.5;
    }

    .thumbnail-container {
      width: 64px;
      height: 64px;
      flex: 0 0 64px;
    }

    .product-details {
      margin-left: 10px;
    }

    .first-product-title {
      font-size: 14px;
      line-height: 1.2;
    }

    .first-product-reviews {
      font-size: 11px;
      line-height: 1.2;
    }

    .first-product-rating-value {
      font-size: 11px;
      line-height: 1.2;
    }

    .first-product-price {
      font-size: 13px;
      line-height: 1.2;
    }

    .circle {
      width: 34px;
      height: 34px;
      flex: 0 0 34px;
      margin-left: 8px;
      font-size: 12px;
    }

    .category-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    .sustainable-craftsmanship-container {
      display: flex;
      flex-direction: column;
      height: auto;
      gap: 12px;
    }
    .fixed-left-card {
      width: 100%;
      height: 320px;
      flex: 0 0 auto;
    }

    .right-container {
      width: 100%;
      height: auto;
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .right-container > * {
      min-height: 220px;
    }

    .recommended-grid {
      grid-template-columns: 1fr;
      gap: 12px;
      margin-top: 16px;
    }
  }

</style>
