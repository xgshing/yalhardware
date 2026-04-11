<!-- 注册页面 -->
<!-- src/views/Register.vue -->
<template>
  <AuthLayout
    :title="purpose"
    :breadcrumb="[{ label: 'Home', clickable: true }, { label: purpose }]"
    @breadcrumb-click="handleClick"
  >
    <!-- 注册表单 -->
    <form
      class="register-box"
      @submit.prevent="submit"
    >
      <div class="input-name">
        <LoginInput
          label="First Name"
          v-model="firstName"
        />
        <LoginInput
          label="Last Name"
          v-model="lastName"
        />
      </div>

      <LoginInput
        label="E-mail"
        v-model="email"
      />
      <LoginInput
        label="Password"
        type="password"
        v-model="password"
      />
      <LoginInput
        label="Confirm Password"
        type="password"
        v-model="confirmPassword"
      />

      <p
        v-if="error"
        class="error"
      >
        {{ error }}
      </p>
      <p v-if="success">{{ success }}</p>

      <div class="choose-btn">
        <button
          type="submit"
          class="btn register-btn"
          :disabled="loading"
        >
          <span class="btn-text">
            {{ loading ? 'Creating Account...' : 'CREATE ACCOUNT' }}
          </span>
          <span class="arrow">→</span>
        </button>

        <button
          type="button"
          class="btn login-btn"
          @click="loginClick"
        >
          <span class="btn-text"> LOG IN </span>
          <span class="arrow">→</span>
        </button>
      </div>
    </form>
  </AuthLayout>
</template>

<script setup lang="ts">
  import { AuthLayout, LoginInput } from '@/components/auth'
  import { computed, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import { registerUser } from '@/services'

  const firstName = ref('')
  const lastName = ref('')
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const error = ref('')
  const success = ref('')
  const loading = ref(false)

  const route = useRoute()
  const router = useRouter()

  /* ================== Purpose 计算属性 ================== */
  const purpose = computed(() => {
    return route.query.purpose as string
  })

  const handleClick = (index: number) => {
    if (index === 0) router.push({ name: 'home' })
  }

  const loginClick = () => {
    router.push({
      name: 'login',
      query: {
        purpose: 'Login',
      },
    })
  }

  /* ================== 表单处理函数 ================== */
  const submit = async () => {
    if (loading.value) return

    // 清空之前的信息
    error.value = ''
    success.value = ''

    // 基础验证：检查必填字段
    if (
      !firstName.value ||
      !lastName.value ||
      !email.value ||
      !password.value ||
      !confirmPassword.value
    ) {
      error.value = 'Please fill in all fields'
      return
    }

    // 密码验证
    if (password.value !== confirmPassword.value) {
      error.value = 'Passwords do not match'
      return
    }

    if (password.value.length < 6) {
      error.value = 'Password must be at least 6 characters'
      return
    }

    // 邮箱校验
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.value)) {
      error.value = 'Please enter a valid email address'
      return
    }

    // 开始加载
    loading.value = true

    try {
      // 准备请求数据
      await registerUser({
        first_name: firstName.value.trim(),
        last_name: lastName.value.trim(),
        email: email.value.trim(),
        password: password.value,
        confirm_password: confirmPassword.value,
      })

      success.value = 'Account created successfully1 Redirecting to login...'

      // 2秒后跳转到登录页面
      setTimeout(() => {
        router.push({
          name: 'login',
          query: {
            purpose: 'Login',
          },
        })
      }, 2000)
    } catch (err: any) {
      const data = err.response?.data
      error.value =
        data?.detail ||
        data?.email?.[0] ||
        data?.password?.[0] ||
        'Registration failed'
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .register-box {
    width: 500px;
    background-color: transparent;
    padding-left: 10px;
  }

  .register-box > * + * {
    margin-top: 12px;
  }

  .input-name {
    display: flex;
    gap: 40px;
  }

  .choose-btn {
    display: flex;
    width: 100%;
    padding: 60px 0;
    gap: 10px;
  }

  .btn {
    display: flex;
    align-items: center;
    justify-content: center;

    flex: 1 1 0; width: auto;
    min-width: 0;
    box-sizing: border-box;

    height: 60px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    gap: 0;
    transition: gap 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .register-btn {
    width: 250px;
    background: #111;
    color: #fff;
    border: none;
  }

  .arrow {
    opacity: 0;
    transform: rotate(-45deg);
    transition:
      opacity 0.2s ease,
      transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* hover：文字 + 箭头整体居中 */
  .btn:hover {
    gap: 15px;
  }

  .btn:hover .arrow {
    opacity: 1;
    transform: rotate(-45deg);
  }

  .login-btn {
    width: 200px;
    background: #ffff;
    color: #333;
    border: 1px solid #999;
  }

  .error {
    color: #d33;
    font-size: 14px;
  }
  @media (max-width: 768px) {
    .register-box {
      width: 320px;
      padding-left: 0;
      margin: 0 auto;
    }
    .choose-btn {
      gap: 10px;
    }
    .btn {
      font-size: 12px;
    }
  }
</style>
