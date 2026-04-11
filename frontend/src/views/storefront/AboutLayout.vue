<template>
  <div class="body">
    <Breadcrumb
      :items="[{ label: 'Home', clickable: true }, { label: purpose }]"
      @item-click="handleClick"
    />

    <div class="about-layout">
      <AboutYalSidebar class="about-sidebar" />

      <div class="about-content">
        <div class="about-switcher">
          <button
            type="button"
            class="about-switcher-btn"
            :class="{ active: purpose === 'About Us' }"
            @click="goToPurpose('About Us')"
          >
            About Us
          </button>
          <button
            type="button"
            class="about-switcher-btn"
            :class="{ active: purpose === 'Contact Us' }"
            @click="goToPurpose('Contact Us')"
          >
            Contact Us
          </button>
        </div>

        <section
          v-if="purpose === 'About Us'"
          class="about-section"
        >
          <h2>About Us</h2>
          <p class="separator-long"></p>

          <div
            class="about-html"
            v-html="company.about_html"
          />
        </section>

        <section
          v-else-if="purpose === 'Contact Us'"
          class="about-section"
        >
          <h2>Contact Us</h2>
          <p class="separator-long"></p>

          <div
            v-if="company"
            class="contact-cards"
          >
            <div class="contact-card">
              <div class="contact-label">Company Name</div>
              <div class="contact-value">{{ company.company_name || '--' }}</div>
            </div>

            <div class="contact-card">
              <div class="contact-label">Address</div>
              <div class="contact-value address">
                {{ company.address || '--' }}
              </div>
            </div>

            <div
              v-if="company.contact_person"
              class="contact-card"
            >
              <div class="contact-label">Contact Person</div>
              <div class="contact-value">{{ company.contact_person }}</div>
            </div>

            <div
              v-if="company.mobile"
              class="contact-card"
            >
              <div class="contact-label">Mob/WeChat</div>
              <div class="contact-value">{{ company.mobile }}</div>
            </div>

            <div
              v-if="company.email"
              class="contact-card"
            >
              <div class="contact-label">Email</div>
              <div class="contact-value">
                <a :href="`mailto:${company.email}`">
                  {{ company.email }}
                </a>
              </div>
            </div>
          </div>

          <div
            v-else
            class="loading"
          >
            Loading contact information...
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import AboutYalSidebar from '@/components/AboutYalSidebar.vue'
  import Breadcrumb from '@/components/Breadcrumb.vue'
  import { getCompanyProfile } from '@/services'
  import { computed, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  const route = useRoute()
  const router = useRouter()

  const company = ref<any>({
    about_html: '',
  })

  const purpose = computed(() => {
    const purposeValue = route.query.purpose as string | undefined
    return purposeValue || 'About Us'
  })

  const handleClick = (index: number) => {
    if (index === 0) {
      router.push({ name: 'home' })
    }
  }

  const goToPurpose = (nextPurpose: 'About Us' | 'Contact Us') => {
    if (purpose.value === nextPurpose) return
    router.push({
      path: '/about',
      query: { purpose: nextPurpose },
    })
  }

  const loadCompanyProfile = async () => {
    company.value = await getCompanyProfile()
  }

  watch(
    () => purpose.value,
    (value) => {
      if (value === 'About Us' || value === 'Contact Us') {
        loadCompanyProfile()
      }
    },
    { immediate: true }
  )
</script>

<style scoped>
  .body {
    min-height: 100vh;
    background-color: #f7f3f3;
  }

  .about-layout {
    display: flex;
    align-items: stretch;
  }

  .about-sidebar {
    flex: 0 0 220px;
  }

  .about-content {
    flex: 1;
    min-width: 0;
    padding: 24px 32px 48px;
    background-color: #f7f3f3;
  }

  .about-switcher {
    display: none;
  }

  .about-section {
    max-width: 920px;
  }

  .about-content h2 {
    margin: 0;
    font-size: 2.5rem;
    line-height: 1.1;
  }

  .separator-long {
    width: 100%;
    height: 1px;
    margin: 12px 0 28px;
    background-color: #ddd;
  }

  .about-html {
    color: #333;
    font-size: 15px;
    line-height: 1.8;
  }

  :deep(.about-html p) {
    margin-bottom: 12px;
  }

  :deep(.about-html img) {
    max-width: 100%;
    height: auto;
    display: inline-block;
    margin: 16px 4px;
  }

  :deep(.about-html img.quill-align-center),
  :deep(.about-html img.ql-align-center) {
    display: block;
    margin-left: auto;
    margin-right: auto;
  }

  :deep(.about-html img.quill-align-left),
  :deep(.about-html img.ql-align-left) {
    float: left;
    margin: 0 1em 1em 0;
  }

  :deep(.about-html img.quill-align-right),
  :deep(.about-html img.ql-align-right) {
    float: right;
    margin: 0 0 1em 1em;
  }

  :deep(.about-html .ql-align-center) {
    text-align: center;
  }

  :deep(.about-html .ql-align-left) {
    text-align: left;
  }

  :deep(.about-html .ql-align-right) {
    text-align: right;
  }

  :deep(.about-html h1),
  :deep(.about-html h2),
  :deep(.about-html h3) {
    margin: 20px 0 12px;
  }

  .contact-cards {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }

  .contact-card {
    padding: 18px 20px;
    border: 1px solid #e4dede;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.78);
    box-shadow: 0 10px 30px rgba(80, 58, 43, 0.06);
  }

  .contact-label {
    margin-bottom: 8px;
    color: #7b6a60;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .contact-value {
    color: #1f2937;
    font-size: 16px;
    line-height: 1.7;
    word-break: break-word;
  }

  .contact-value a {
    color: inherit;
    text-decoration: underline;
    text-underline-offset: 3px;
  }

  .address {
    white-space: pre-line;
  }

  .loading {
    color: #6b7280;
    font-size: 15px;
  }

  @media (max-width: 768px) {
    .about-layout {
      display: block;
    }

    .about-sidebar {
      display: none;
    }

    .about-content {
      padding: 16px 16px 32px;
    }

    .about-switcher {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }

    .about-switcher-btn {
      height: 44px;
      border: 1px solid #d9ccc3;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.92);
      color: #6b5b51;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition:
        background-color 0.18s ease,
        border-color 0.18s ease,
        color 0.18s ease;
    }

    .about-switcher-btn.active {
      border-color: #2b211a;
      background: #2b211a;
      color: #fff;
    }

    .about-content h2 {
      font-size: 1.75rem;
      line-height: 1.2;
    }

    .separator-long {
      margin: 10px 0 18px;
    }

    .about-html {
      font-size: 14px;
      line-height: 1.85;
    }

    :deep(.about-html img) {
      display: block;
      float: none !important;
      margin: 16px auto;
      width: auto;
      max-width: 100%;
      height: auto;
    }

    :deep(.about-html .ql-align-left),
    :deep(.about-html .ql-align-right),
    :deep(.about-html .ql-align-center) {
      text-align: center;
    }

    .contact-cards {
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .contact-card {
      padding: 16px;
      border-radius: 14px;
    }

    .contact-value {
      font-size: 15px;
    }
  }
</style>
