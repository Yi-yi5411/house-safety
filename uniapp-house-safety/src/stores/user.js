/**
 * User state management — Pinia store.
 * Manages authentication state, user profile, and token.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCurrentUser } from '@/api/auth.js'

export const useUserStore = defineStore('user', () => {
  // ---- State ----
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref(uni.getStorageSync('userInfo') || null)
  const isLoggedIn = computed(() => !!token.value)

  // ---- Actions ----
  function setToken(newToken) {
    token.value = newToken
    uni.setStorageSync('token', newToken)
  }

  function setUserInfo(info) {
    userInfo.value = info
    uni.setStorageSync('userInfo', info)
  }

  async function fetchUserInfo() {
    try {
      const res = await getCurrentUser()
      if (res) {
        setUserInfo(res)
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }

  function login(loginToken, info) {
    setToken(loginToken)
    if (info) {
      setUserInfo(info)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    setToken,
    setUserInfo,
    fetchUserInfo,
    login,
    logout
  }
})
