<!-- src/components/NavBar.vue -->
<template>
  <div ref="navRootRef">
    <header :class="['header', { 'header-hidden': !isNavVisible }]">
      <div class="nav-container">
        <!-- 移动端菜单按钮（放在 LOGO 左侧） -->
        <button
          class="mobile-menu-btn"
          @click="toggleMobileMenu"
          aria-label="Open menu"
        >
          &#9776;
        </button>

        <!-- Logo -->
        <div
          class="logo"
          @click="goHome"
        >
          <span>{{ logo.text }}</span>
        </div>

        <!-- 桌面导航菜单 -->
        <ul class="nav-menu">
          <li
            v-for="item in menuItems"
            :key="item.id"
            class="nav-item"
            @mouseenter="handleMouseEnter(item.id)"
            @mouseleave="handleMouseLeave(item.id)"
          >
            <a
              href="#"
              class="nav-link"
              @click.prevent="handleMenuItemClick(item)"
            >
              {{ item.text }}
              <span
                v-if="item.hasDropdown"
                class="dropdown-icon"
                >▼</span
              >
            </a>

            <div
              v-if="item.hasDropdown && dropdownStates[item.id]"
              class="dropdown-menu"
            >
              <a
                v-for="subItem in item.subItems"
                :key="subItem.id"
                href="#"
                class="dropdown-item"
                @click.prevent="handleSubItemClick(subItem)"
              >
                {{ subItem.text }}
              </a>
            </div>
          </li>
        </ul>

        <div
          class="nav-link about-link"
          @click="openAboutUs"
        >
          About Us
        </div>

        <!-- 桌面右侧功能 -->
        <div class="nav-right">
          <button
            type="button"
            class="search"
            @click="openSearchPanel"
          >
            <span class="rotate-char">&#8981;</span>
            <span class="search-text">Search</span>
          </button>

          <!-- Account 下拉菜单 -->
          <div class="account-dropdown-wrapper">
            <a
              class="account"
              @click="toggleDropdown"
            >
              {{ accountLabel }}
            </a>

            <div
              v-if="isOpen"
              class="account-dropdown"
            >
              <!-- 未登录 -->
              <template v-if="!canAccessOrders">
                <div
                  class="dropdown-item"
                  @click="handleLogin"
                >
                  Log In
                </div>
                <div
                  class="dropdown-item"
                  @click="handleCreateAccount"
                >
                  Create Account
                </div>
              </template>

              <template v-else-if="isLoggedIn">
                <div
                  class="dropdown-item"
                  @click="goProfile"
                >
                  Hello, {{ userFullName }}
                </div>
                <div
                  class="dropdown-item"
                  @click="gooders"
                >
                  My Orders
                </div>
                <div
                  class="dropdown-item"
                  @click="handleLogout"
                >
                  Log Out
                </div>
              </template>
              <template v-else>
                <div
                  class="dropdown-item"
                  @click="gooders"
                >
                  My Orders
                </div>
              </template>
            </div>
          </div>

          <div
            class="cart"
            @click="openCart"
          >
            <a>Cart</a>
            <div
              class="circle"
              v-if="cartStore.totalItems > 0"
            >
              {{ cartStore.totalItems }}
            </div>
          </div>
        </div>
      </div>
    </header>

    <transition name="search-panel-fade">
      <section
        v-if="isSearchOpen"
        ref="searchPanelRef"
        class="search-panel"
      >
        <div class="search-panel-title">Search</div>

        <div class="search-bar-row">
          <input
            ref="searchInputRef"
            v-model="searchKeyword"
            class="search-input"
            type="text"
            placeholder="What are You Looking For ..."
            @input="onSearchInput"
            @keydown.enter.prevent="submitSearch"
          />
          <button
            type="button"
            class="search-submit-btn"
            @click="submitSearch"
          >
            SEARCH
          </button>
        </div>

        <div class="search-products-header">
          <span>Products</span>
        </div>

        <div
          v-if="searchKeyword.trim() && suggestedProducts.length > 0"
          class="search-products-grid"
        >
          <ProductCard
            v-for="product in suggestedProducts"
            :key="product.id"
            class="search-product-item"
            :product-data="product"
            :current-image="getCardImage(product)"
            @product-click="openSuggestedProduct"
          />
        </div>

        <div
          v-else-if="searchKeyword.trim() && !isSearching"
          class="search-empty"
        >
          No matching products found.
        </div>

        <div
          v-else-if="isSearching"
          class="search-empty"
        >
          Searching...
        </div>
      </section>
    </transition>

    <transition name="mobile-menu-fade">
      <div
        v-if="isMobileMenuOpen"
        class="mobile-menu-backdrop"
        @click="closeMobileMenu"
      ></div>
    </transition>

    <transition name="mobile-menu-fade">
      <div
        v-if="isMobileMenuOpen"
        class="mobile-menu-panel"
      >
        <ul class="mobile-nav-list">
          <li
            v-for="item in menuItems"
            :key="item.id"
            class="mobile-nav-item"
          >
            <button
              class="mobile-nav-link"
              @click="handleMenuItemClick(item)"
            >
              <span>{{ item.text }}</span>
              <span
                v-if="item.hasDropdown"
                class="mobile-dropdown-icon"
                :class="{ open: dropdownStates[item.id] }"
              >
                ▼
              </span>
            </button>

            <div
              v-if="
                item.hasDropdown &&
                dropdownStates[item.id] &&
                item.subItems.length > 0
              "
              class="mobile-submenu"
            >
              <button
                v-for="subItem in item.subItems"
                :key="subItem.id"
                class="mobile-submenu-item"
                @click="handleSubItemClick(subItem)"
              >
                {{ subItem.text }}
              </button>
            </div>
          </li>

          <li class="mobile-nav-item">
            <button
              class="mobile-nav-link"
              @click="openAboutUs(); closeMobileMenu()"
            >
              About Us
            </button>
          </li>

        </ul>
      </div>
    </transition>

    <!-- 占位元素 -->
    <div class="nav-placeholder"></div>
  </div>
</template>

<script setup lang="ts">
  import { frontendProductApi } from '@/api'
  import ProductCard from '@/components/ProductCard.vue'
  import { PRODUCT_PLACEHOLDER_IMAGE } from '@/constants/images'
  import { fetchCategoryTree } from '@/services'
  import { useCartStore } from '@/stores/cart'
  import { useUserStore } from '@/stores/user'
  import type { Product } from '@/types'
  import { getPrimaryImage } from '@/utils/images'
  import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
  import { useRouter } from 'vue-router'

  const router = useRouter()
  const logo = reactive({ text: 'YAL Industrial & Trading' })
  const BYPASS_USER_AUTH = import.meta.env.VITE_BYPASS_USER_AUTH === 'true'
  const navRootRef = ref<HTMLElement | null>(null)
  const searchInputRef = ref<HTMLInputElement | null>(null)
  const searchPanelRef = ref<HTMLElement | null>(null)

  // ================== 导航滚动 ==================
  const isNavVisible = ref(true)
  const lastScrollTop = ref(0)
  const hasScrolled = ref(false)

  // ================== 菜单 ==================
  interface SubItem {
    id: number
    text: string
  }
  interface MenuItems {
    id: number
    text: string
    hasDropdown: boolean
    subItems: SubItem[]
  }

  const menuItems = ref<MenuItems[]>([])
  const dropdownStates = reactive<Record<number, boolean>>({})

  // ================== Search ==================
  const isSearchOpen = ref(false)
  const searchKeyword = ref('')
  const suggestedProducts = ref<Product[]>([])
  const isSearching = ref(false)
  let searchTimer: ReturnType<typeof setTimeout> | null = null
  let latestSearchRequestId = 0

  // ================== 关于公司 ==================
  const openAboutUs = () =>
    router.push({ name: 'about', query: { purpose: 'About Us' } })
  const goHome = () => {
    closeSearchPanel()
    closeMobileMenu()
    router.push({ name: 'home' })
  }

  // ================== 购物车 ==================
  const cartStore = useCartStore()
  const openCart = () =>
    router.push({ name: 'cart', query: { purpose: 'Your Shopping Cart' } })

  // ================== 用户 ==================
  const userStore = useUserStore()

  // computed
  const isLoggedIn = computed(() => userStore.role === 'user')
  const userFullName = computed(() => userStore.fullName)
  const canAccessOrders = computed(() => isLoggedIn.value || BYPASS_USER_AUTH)
  const accountLabel = computed(() => {
    if (isLoggedIn.value) return userFullName.value
    if (BYPASS_USER_AUTH) return 'Test_user'
    return 'Account'
  })

  // 下拉状态
  const isOpen = ref(false)
  const toggleDropdown = () => {
    isOpen.value = !isOpen.value
  }

  // ================== 导航跳转 ==================
  const handleLogin = () => {
    router.push({ name: 'login', query: { purpose: 'Login' } })
    isOpen.value = false
  }
  const handleCreateAccount = () => {
    router.push({ name: 'register', query: { purpose: 'Create Account' } })
    isOpen.value = false
  }
  const goProfile = () => {
    router.push({ name: 'profile' })
    isOpen.value = false
  }
  const gooders = () => {
    router.push({ name: 'order-list' })
    isOpen.value = false
  }
  const handleLogout = () => {
    userStore.logout()
    isOpen.value = false
    router.push({ name: 'home' })
  }
  // ================== 获取后台分类 ==================
  async function fetchCategories() {
    const data = await fetchCategoryTree()
    menuItems.value = data.map((cat: any) => ({
      id: cat.id,
      text: cat.name,
      hasDropdown: Array.isArray(cat.children) && cat.children.length > 0,
      subItems: (cat.children || []).map((sub: any) => ({
        id: sub.id,
        text: sub.name,
      })),
    }))
  }

  // ================== 页面滚动 ==================
  function handleScroll() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    hasScrolled.value = scrollTop > 10
    if (scrollTop > lastScrollTop.value && scrollTop > 100)
      isNavVisible.value = false
    else if (scrollTop < lastScrollTop.value) isNavVisible.value = true
    lastScrollTop.value = scrollTop <= 0 ? 0 : scrollTop
  }
  function debounce(func: Function, wait: number) {
    let timeout: number | undefined
    return function executedFunction(...args: any) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }

  // ================== 鼠标与移动端 ==================
  const isMobileMenuOpen = ref(false)
  const setPageScrollLock = (locked: boolean) => {
    const value = locked ? 'hidden' : ''
    document.documentElement.style.overflow = value
    document.body.style.overflow = value
    document.body.style.touchAction = ''
  }
  const syncPageScrollLock = () => {
    const shouldLock = isSearchOpen.value || (isMobileView() && isMobileMenuOpen.value)
    setPageScrollLock(shouldLock)
  }
  const toggleMobileMenu = () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
  }
  const closeMobileMenu = () => {
    isMobileMenuOpen.value = false
  }
  const isMobileView = () => window.innerWidth <= 768
  const handleMouseEnter = (id: number) => {
    if (!isMobileView()) dropdownStates[id] = true
  }
  const handleMouseLeave = (id: number) => {
    if (!isMobileView()) dropdownStates[id] = false
  }

  // 菜单点击
  function handleMenuItemClick(item: MenuItems) {
    if (item.hasDropdown && isMobileView()) {
      dropdownStates[item.id] = !dropdownStates[item.id]
      return
    }
    if (item.hasDropdown) return
    router.push({ name: 'product-categories', query: { category: item.text } })
    closeMobileMenu()
  }
  function handleSubItemClick(subItem: SubItem) {
    router.push({
      name: 'product-categories',
      query: { category: subItem.text },
    })
    closeMobileMenu()
  }

  function getCardImage(product: Product): string {
    return getPrimaryImage(product) || PRODUCT_PLACEHOLDER_IMAGE
  }

  function openSearchPanel() {
    if (isSearchOpen.value) {
      closeSearchPanel()
      return
    }
    isSearchOpen.value = true
    closeMobileMenu()
    suggestedProducts.value = []
    setTimeout(() => searchInputRef.value?.focus(), 0)
  }

  function closeSearchPanel() {
    isSearchOpen.value = false
  }

  async function fetchSearchSuggestions() {
    const q = searchKeyword.value.trim()
    if (!q) {
      suggestedProducts.value = []
      isSearching.value = false
      return
    }

    const requestId = ++latestSearchRequestId
    isSearching.value = true
    try {
      const res = await frontendProductApi.list({ q, limit: 8 })
      if (requestId !== latestSearchRequestId) return
      suggestedProducts.value = res.data || []
    } catch {
      if (requestId !== latestSearchRequestId) return
      suggestedProducts.value = []
    } finally {
      if (requestId === latestSearchRequestId) {
        isSearching.value = false
      }
    }
  }

  function onSearchInput() {
    if (!searchKeyword.value.trim()) {
      if (searchTimer) clearTimeout(searchTimer)
      suggestedProducts.value = []
      isSearching.value = false
      return
    }
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(fetchSearchSuggestions, 250)
  }

  function submitSearch() {
    const q = searchKeyword.value.trim()
    if (!q) return
    closeSearchPanel()
    router.push({
      name: 'product-categories',
      query: { q },
    })
  }

  function openSuggestedProduct(product: Product) {
    closeSearchPanel()
    router.push({
      name: 'product-detail',
      params: {
        category: product.category?.name || 'all',
        id: String(product.id),
      },
    })
  }

  function handleGlobalClick(event: MouseEvent) {
    if (!isSearchOpen.value) return
    const panel = searchPanelRef.value
    const target = event.target as Node | null
    if (!target) return
    if (panel?.contains(target)) return
    closeSearchPanel()
  }

  function handleGlobalKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      closeSearchPanel()
    }
  }

  // ================== 生命周期 ==================
  onMounted(() => {
    fetchCategories()
    const debouncedScroll = debounce(handleScroll, 10)
    window.addEventListener('scroll', debouncedScroll)
    document.addEventListener('mousedown', handleGlobalClick)
    document.addEventListener('keydown', handleGlobalKeydown)
  })
  onUnmounted(() => {
    setPageScrollLock(false)
    const debouncedScroll = debounce(handleScroll, 10)
    window.removeEventListener('scroll', debouncedScroll)
    document.removeEventListener('mousedown', handleGlobalClick)
    document.removeEventListener('keydown', handleGlobalKeydown)
    if (searchTimer) clearTimeout(searchTimer)
  })

  // ================== watch 用户状态 ==================
  watch(
    () => userStore.user,
    () => {},
    { immediate: true }
  )

  watch(
    isMobileMenuOpen,
    () => {
      syncPageScrollLock()
    },
    { immediate: true }
  )

  watch(isSearchOpen, (open) => {
    if (open) onSearchInput()
    syncPageScrollLock()
  })
</script>

<style scoped>
  /* 导航栏样式 */
  /* 导航栏动效时间 */
  .header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 50;
    background-color: white;
    transition:
      transform 0.4s ease,
      box-shadow 0.3s ease;
    transform: translateY(0);
    display: flex;
    align-items: center;
    width: 100%;
    height: 70px;
  }

  /* 隐藏状态 */
  .header-hidden {
    transform: translateY(-100%);
  }

  .nav-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    /* 关键：使用 space-between 控制分布 */
    width: 100%;
    padding: 0 30px;
    flex-wrap: nowrap;
    gap: 12px;
  }

  .logo {
    font-size: 22px;
    font-weight: 700;
    cursor: pointer;
  }

  /* 桌面导航菜单 */
  .nav-menu {
    display: flex;
    list-style: none;
  }

  /* 移动端隐藏桌面菜单 */
  @media (max-width: 768px) {
    .nav-menu {
      display: none;
    }
  }

  .nav-item {
    position: relative;
  }

  .nav-link {
    color: black;
    text-decoration: none;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    border-radius: 6px;
    transition: all 0.3s ease;
    font-size: 16px;
    font-weight: 500;
    white-space: nowrap;
    cursor: pointer;
  }

  .nav-link:hover {
    background-color: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
  }

  .dropdown-icon {
    margin-left: 8px;
    font-size: 12px;
    transition: transform 0.3s ease;
  }

  .nav-item:hover .dropdown-icon {
    transform: rotate(180deg);
  }

  /* 下拉菜单 */
  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    background-color: white;
    min-width: 220px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    border-radius: 8px;
    padding: 8px 0;
    z-index: 1000;
    border: 1px solid #e1e5e9;
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    color: #333;
    text-decoration: none;
    transition: all 0.2s ease;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
  }

  .dropdown-item:hover {
    background: linear-gradient(135deg, #f0f5ff 0%, #e6eeff 100%);
    color: #2575fc;
    padding-left: 25px;
  }

  /* 桌面导航：搜索、账户、购物车 */
  .nav-right {
    display: flex;
    align-items: center;
    gap: 30px;
    margin-left: auto;
  }

  .search {
    border: none;
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    padding: 0;
    font-family: inherit;
    line-height: 1;
  }

  .search-text {
    font-size: 16px;
    line-height: 1;
  }

  .rotate-char {
    display: inline-block;
    transform: rotate(-90deg);
    /* 逆时针旋转 90 度 */
    font-size: 24px;
    margin-right: 10px;
  }

  .search-panel {
    position: fixed;
    top: 70px;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 45;
    background: #fff;
    border-top: 1px solid #e5e7eb;
    box-shadow: 0 20px 35px rgba(17, 24, 39, 0.08);
    padding: 28px 150px calc(26px + env(safe-area-inset-bottom));
    box-sizing: border-box;
    overflow-y: auto;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
  }

  .search-panel-title {
    font-size: 44px;
    line-height: 1;
    margin-bottom: 18px;
    font-weight: 500;
  }

  .search-bar-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 190px;
    gap: 12px;
    align-items: center;
  }

  .search-input {
    width: 100%;
    height: 60px;
    border: 1px solid #b58c72;
    border-radius: 4px;
    font-size: 22px;
    padding: 0 16px;
    color: #1f2937;
    box-sizing: border-box;
    outline: none;
  }

  .search-input::placeholder {
    color: #9ca3af;
    font-size: 14px;
  }

  .search-submit-btn {
    height: 60px;
    border: none;
    border-radius: 4px;
    background: #1f1f1f;
    color: #fff;
    font-weight: 700;
    letter-spacing: 0.04em;
    cursor: pointer;
  }

  .search-products-header {
    margin-top: 22px;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 10px;
    color: #374151;
    font-size: 20px;
    position: relative;
  }

  .search-products-header span::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -1px;
    width: 72px;
    height: 2px;
    background: #b58c72;
  }

  .search-products-grid {
    margin-top: 26px;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 18px;
  }

  .search-empty {
    margin-top: 20px;
    color: #6b7280;
    font-size: 16px;
  }

  /* ============================ 用户登录 ============================ */
  /* 容器保持相对定位，便于下拉菜单绝对定位 */
  .account-dropdown-wrapper {
    position: relative;
    display: inline-block;
    cursor: pointer;
  }
  .account {
    font-size: 16px;
    line-height: 1;
  }
  /* 下拉菜单定位在 Account 下方 */
  .account-dropdown {
    position: absolute;
    top: 100%;
    /* 下方紧贴 Account */
    right: 0;
    /* 右侧对齐 Account */
    background-color: white;
    border: 1px solid #ddd;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    width: 150px;
    z-index: 1000;
  }

  /* 下拉项样式 */
  .account-dropdown .dropdown-item {
    padding: 10px 15px;
    cursor: pointer;
  }

  .account-dropdown .dropdown-item:hover {
    background-color: #f0f0f0;
  }

  .cart {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
  }

  .cart a {
    font-size: 16px;
    font-family: inherit;
    line-height: 1;
  }

  .mobile-account-entry {
    display: none;
    border: none;
    background: transparent;
    color: #111827;
    font-size: 14px;
    line-height: 1;
    padding: 0;
    cursor: pointer;
    white-space: nowrap;
  }

  .circle {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: 1px solid #ccc;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 14px;
    color: #333;
    transition: 0.3s;
  }

  /* 悬停整个 cart 时生效 */
  .cart:hover .circle {
    background: #000;
    border-color: #000;
    color: #fff;
  }

  /* 移动端菜单按钮 */
  .mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    color: black;
    font-size: 24px;
    padding: 0;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.3s ease;
  }

  .mobile-menu-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .mobile-menu-panel {
    display: none;
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    z-index: 49;
    background: #fff;
    border-top: 1px solid #eee;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    max-height: calc(100vh - 60px);
    overflow-y: auto;
  }

  .mobile-menu-backdrop {
    display: none;
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 48;
    background: rgba(0, 0, 0, 0.35);
  }

  .mobile-nav-list {
    list-style: none;
    margin: 0;
    padding: 8px 0;
  }

  .mobile-nav-item {
    border-bottom: 1px solid #f0f0f0;
  }

  .mobile-nav-link {
    width: 100%;
    padding: 14px 16px;
    border: none;
    background: #fff;
    color: #222;
    font-size: 15px;
    text-align: left;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
  }

  .mobile-dropdown-icon {
    font-size: 11px;
    transition: transform 0.2s ease;
  }

  .mobile-dropdown-icon.open {
    transform: rotate(180deg);
  }

  .mobile-submenu {
    background: #fafafa;
    padding: 4px 0 8px;
  }

  .mobile-submenu-item {
    width: 100%;
    border: none;
    background: transparent;
    text-align: left;
    padding: 10px 28px;
    color: #444;
    font-size: 14px;
    cursor: pointer;
  }

  .mobile-menu-fade-enter-active,
  .mobile-menu-fade-leave-active {
    transition: opacity 0.18s ease;
  }

  .mobile-menu-fade-enter-from,
  .mobile-menu-fade-leave-to {
    opacity: 0;
  }

  .search-panel-fade-enter-active,
  .search-panel-fade-leave-active {
    transition:
      opacity 0.18s ease,
      transform 0.18s ease;
  }

  .search-panel-fade-enter-from,
  .search-panel-fade-leave-to {
    opacity: 0;
    transform: translateY(-8px);
  }

  /* 占位元素：与导航栏同高 */
  .nav-placeholder {
    height: 70px;
    width: 100%;
    background: transparent;
  }

  /* 响应式设置 */
  @media (max-width: 768px) {
    .header {
      height: 60px;
    }

    .nav-placeholder {
      height: 60px;
    }

    .nav-menu {
      display: none;
    }

    /* 移动端：菜单按钮显示在左侧 */
    .mobile-menu-btn {
      display: block;
      order: 0;
      font-size: 20px; /* 图标大小 */
      width:20px;     /* 按钮点击区域宽 */
      height: 20px;    /* 按钮点击区域高 */

      line-height: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
    }

    /* 移动端：Search 仅显示图标 */
    .search-text {
      display: none;
    }
    .cart a {
      display: none;
    }
    .circle {
      width: 20px;
      height: 20px;
    }
      /* 移动端收紧左右 padding，避免横向溢出 */
    .nav-container {
      padding: 0 20px;
      gap: 8px;
    }

    .search-panel {
      top: 60px;
      bottom: 0;
      left: 20px;
      right: 20px;
      padding: 18px 0 calc(20px + env(safe-area-inset-bottom));
    }

    .search-panel-title {
      font-size: 30px;
      margin-bottom: 12px;
    }

    .search-bar-row {
      grid-template-columns: 1fr;
      gap: 8px;
    }

    .search-input,
    .search-submit-btn {
      height: 48px;
    }

    .search-input {
      font-size: 18px;
    }

    .search-products-header {
      margin-top: 14px;
      font-size: 16px;
    }

    .search-products-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 16px;
    }

    .logo {
      font-size: 14px;
      font-weight: 700;
      white-space: nowrap;
      overflow: visible;
      text-overflow: clip;
      min-width: fit-content;
      flex: 0 0 auto;
      margin-right: auto;
    }

    .about-link {
      display: none;
    }

    .account-dropdown-wrapper {
      display: inline-block;
    }

    .account {
      display: inline-flex;
      align-items: center;
      font-size: 14px;
      line-height: 1;
      white-space: nowrap;
    }

    .nav-right {
      gap: 8px;
      margin-left: 8px;
    }

    .mobile-menu-panel {
      display: block;
    }

    .mobile-menu-backdrop {
      display: block;
    }
  }
</style>
