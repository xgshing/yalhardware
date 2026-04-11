// src/utils/request.ts
import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios'

import {
  clearAdminToken,
  clearUserToken,
  getAdminAccessToken,
  getAdminRefreshToken,
  getUserAccessToken,
  getUserRefreshToken,
  setAdminToken,
  setUserToken,
} from './auth'
import { isTokenExpiringSoon } from './jwt'

// 从环境变量中获取API 基础地址
const BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/api`

/**
 * 创建带自动刷新 token 功能的 axios 实例
 * @param options - 配置对象，包含获取/设置/清除 token 的方法
 * @returns 配置好的 axios 实例
 */
function createAuthInstance(options: {
  getAccess: () => string | null
  getRefresh: () => string | null
  setToken: (access: string, refresh: string) => void
  clearToken: () => void
}): AxiosInstance {
  // 创建 axios 实例
  const instance = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
  })

  // 刷新锁标志：防止多个请求同时刷新 token
  let refreshing = false
  // 请求队列：存储等待 token 刷新的请求
  let queue: Array<(token: string | null) => void> = []

  /**
   * 处理排队中的请求
   * @param token - 刷新后的新 token（如果失败则为 null）
   */
  function resolveQueue(token: string | null) {
    queue.forEach((cb) => cb(token)) // 依次执行队列中的回调
    queue = [] // 清空队列
  }

  /**
   * 获取可用的 access token（必要时会刷新，并对并发做排队）
   */
  async function getValidAccessToken(): Promise<string | null> {
    const current = options.getAccess()
    if (!current) return null
    if (!isTokenExpiringSoon(current, 60)) return current

    if (!refreshing) {
      refreshing = true
      const newToken = await refreshToken()
      resolveQueue(newToken)
      refreshing = false
      return newToken
    }

    return await new Promise((resolve) => {
      queue.push(resolve)
    })
  }

  /**
   * 刷新 access token
   * @returns 新的 access token，失败则返回 null
   */
  async function refreshToken(): Promise<string | null> {
    const refresh = options.getRefresh() // 获取 refresh token
    if (!refresh) return null // 没有 refresh token 则无法刷新

    try {
      // 调用刷新 token 的接口
      const res = await axios.post(`${BASE_URL}/auth/refresh/`, {
        refresh,
      })
      const newAccess = res.data.access as string // 获取新的 access token
      options.setToken(newAccess, refresh) // 保存新 token
      return newAccess // 返回新 token
    } catch {
      // 刷新失败（refresh token 可能已过期），清除本地 token
      options.clearToken()
      return null
    }
  }

  // ================= 请求拦截（主动提前刷新） =================
  /**
   * 请求拦截器：在发送请求前检查 token 是否快过期
   * 如果快过期，主动刷新 token，避免请求失败
   */
  instance.interceptors.request.use(async (config) => {
    const token = await getValidAccessToken()

    // 如果有 token，添加到请求头
    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config // 继续发送请求
  })

  // ================= 响应拦截（401 被动兜底） =================
  /**
   * 响应拦截器：处理 401 未授权错误
   * 如果遇到 401，尝试刷新 token 后重试请求
   */
  instance.interceptors.response.use(
    (res) => res,
    // 正常响应直接返回
    async (error: AxiosError) => {
      // 获取原始请求配置
      const original = error.config as
        | (InternalAxiosRequestConfig & { _retry?: boolean })
        | undefined

      // 如果没有请求配置，或者不是 401 错误，或者已经重试过，直接返回错误
      if (!original || error.response?.status !== 401 || original._retry) {
        return Promise.reject(error)
      }

      original._retry = true // 标记已经重试过，防止无限循环

      // 如果已经在刷新 token，等待刷新完成
      if (refreshing) {
        return new Promise((resolve, reject) => {
          queue.push((token) => {
            if (!token) return reject(error) // 刷新失败
            original.headers = original.headers ?? {}
            original.headers.Authorization = `Bearer ${token}` // 添加新 token
            resolve(instance(original)) // 重试原始请求
          })
        })
      }

      // 开始刷新 token
      refreshing = true
      const newToken = await refreshToken()
      resolveQueue(newToken) // 处理排队请求
      refreshing = false

      // 如果刷新失败，返回错误
      if (!newToken) return Promise.reject(error)

      // 使用新 token 重试原始请求
      original.headers = original.headers ?? {}
      original.headers.Authorization = `Bearer ${newToken}`
      return instance(original) // 返回配置好的实例
    }
  )

  return instance
}

/**
 * 前台用户请求实例
 * 用于普通用户的 API 请求
 * 使用前台用户的 token 进行认证
 */
export const frontendRequest = createAuthInstance({
  getAccess: getUserAccessToken, // 获取前台 access token
  getRefresh: getUserRefreshToken, // 获取前台 refresh token
  setToken: setUserToken, // 保存前台 token
  clearToken: clearUserToken, // 清除前台 token
})

/**
 * 后台管理员请求实例
 * 用于管理员后台的 API 请求
 * 使用管理员的 token 进行认证
 */
export const adminRequest = createAuthInstance({
  getAccess: getAdminAccessToken, // 获取后台 access token
  getRefresh: getAdminRefreshToken, // 获取后台 refresh token
  setToken: setAdminToken, // 保存后台 token
  clearToken: clearAdminToken, // 清除后台 token
})
