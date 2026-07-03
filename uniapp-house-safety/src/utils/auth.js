// 登录状态管理

const TOKEN_KEY = 'token'
const USER_INFO_KEY = 'userInfo'
const LOGIN_STATUS_KEY = 'loginStatus'

// 设置登录状态
export function setLoginStatus(status) {
  uni.setStorageSync(LOGIN_STATUS_KEY, status)
}

// 获取登录状态
export function getLoginStatus() {
  return uni.getStorageSync(LOGIN_STATUS_KEY) || false
}

// 设置用户信息
export function setUserInfo(userInfo) {
  uni.setStorageSync(USER_INFO_KEY, userInfo)
}

// 获取用户信息
export function getUserInfo() {
  return uni.getStorageSync(USER_INFO_KEY) || null
}

// 设置 Token
export function setToken(token) {
  uni.setStorageSync(TOKEN_KEY, token)
}

// 获取 Token
export function getToken() {
  return uni.getStorageSync(TOKEN_KEY) || ''
}

// 清除登录信息
export function clearLoginInfo() {
  uni.removeStorageSync(TOKEN_KEY)
  uni.removeStorageSync(USER_INFO_KEY)
  uni.removeStorageSync(LOGIN_STATUS_KEY)
}

// 检查登录状态
export function checkLoginStatus() {
  const isLoggedIn = getLoginStatus()
  if (!isLoggedIn) {
    uni.reLaunch({ url: '/pages/login/login' })
    return false
  }
  return true
}

// 需要登录的页面守卫
export function requireLogin() {
  return new Promise((resolve) => {
    const isLoggedIn = getLoginStatus()
    if (!isLoggedIn) {
      uni.showModal({
        title: '提示',
        content: '请先登录',
        showCancel: false,
        success: () => {
          uni.reLaunch({ url: '/pages/login/login' })
          resolve(false)
        }
      })
    } else {
      resolve(true)
    }
  })
}
