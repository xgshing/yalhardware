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

const BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/api`

function createAuthInstance(options: {
  getAccess: () => string | null
  getRefresh: () => string | null
  setToken: (access: string, refresh: string) => void
  clearToken: () => void
}): AxiosInstance {
  const instance = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
  })

  let refreshing = false
  let queue: Array<(token: string | null) => void> = []

  function resolveQueue(token: string | null) {
    queue.forEach((cb) => cb(token))
    queue = []
  }

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

  async function refreshToken(): Promise<string | null> {
    const refresh = options.getRefresh()
    if (!refresh) return null

    try {
      const res = await axios.post(`${BASE_URL}/token/refresh/`, {
        refresh,
      })
      const newAccess = res.data.access as string
      options.setToken(newAccess, refresh)
      return newAccess
    } catch {
      options.clearToken()
      return null
    }
  }

  instance.interceptors.request.use(async (config) => {
    const token = await getValidAccessToken()

    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  })

  instance.interceptors.response.use(
    (res) => res,
    async (error: AxiosError) => {
      const original = error.config as
        | (InternalAxiosRequestConfig & { _retry?: boolean })
        | undefined

      if (!original || error.response?.status !== 401 || original._retry) {
        return Promise.reject(error)
      }

      original._retry = true

      if (refreshing) {
        return new Promise((resolve, reject) => {
          queue.push((token) => {
            if (!token) return reject(error)
            original.headers = original.headers ?? {}
            original.headers.Authorization = `Bearer ${token}`
            resolve(instance(original))
          })
        })
      }

      refreshing = true
      const newToken = await refreshToken()
      resolveQueue(newToken)
      refreshing = false

      if (!newToken) return Promise.reject(error)

      original.headers = original.headers ?? {}
      original.headers.Authorization = `Bearer ${newToken}`
      return instance(original)
    }
  )

  return instance
}

export const frontendRequest = createAuthInstance({
  getAccess: getUserAccessToken,
  getRefresh: getUserRefreshToken,
  setToken: setUserToken,
  clearToken: clearUserToken,
})

export const adminRequest = createAuthInstance({
  getAccess: getAdminAccessToken,
  getRefresh: getAdminRefreshToken,
  setToken: setAdminToken,
  clearToken: clearAdminToken,
})
