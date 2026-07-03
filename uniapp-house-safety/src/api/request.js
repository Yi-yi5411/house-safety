// API Base URL - points to FastAPI backend
const BASE_URL = 'http://127.0.0.1:8000/api/v1'

/**
 * HTTP request wrapper for uni-app.
 * Backend returns raw Pydantic models (no {code, message, data} wrapper),
 * so we pass the response data through directly on 200.
 */
function request(options) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const header = {
      'Content-Type': 'application/json',
      ...options.header
    }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header,
      success: (res) => {
        const { statusCode, data } = res

        if (statusCode === 200 || statusCode === 201) {
          // Handle both wrapped {code,data,message} and raw response formats
          if (data && typeof data === 'object' && 'code' in data && 'data' in data) {
            // Wrapped format: {code: 200, data: ..., message: "..."}
            if (data.code === 200 || data.code === 0 || data.code === 201) {
              resolve(data.data)
            } else {
              const msg = typeof data.message === 'string' ? data.message : (Array.isArray(data.message) ? data.message.map(e => e.msg || JSON.stringify(e)).join('; ') : '请求失败')
              uni.showToast({ title: msg, icon: 'none' })
              reject(new Error(msg))
            }
          } else {
            // Raw format: pass through directly
            resolve(data)
          }
        } else if (statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/login/login' })
          }, 1500)
          reject(new Error('Unauthorized'))
        } else if (statusCode === 204) {
          resolve(null)
        } else {
          let message = (data && data.message) || (data && data.detail) || '服务器错误'
          if (Array.isArray(message)) {
            message = message.map(e => e.msg || JSON.stringify(e)).join('; ')
          } else if (typeof message !== 'string') {
            message = JSON.stringify(message)
          }
          uni.showToast({ title: message, icon: 'none' })
          reject(new Error(typeof message === 'string' ? message : JSON.stringify(message)))
        }
      },
      fail: (err) => {
        const msg = err.errMsg || '网络请求失败'
        console.error('Request failed:', options.url, msg)
        uni.showToast({ title: msg.includes('timeout') ? '请求超时，请检查代理设置' : msg, icon: 'none', duration: 3000 })
        reject(err)
      }
    })
  })
}

/**
 * File upload helper using uni.uploadFile.
 */
function uploadFile(filePath, url = '/upload/image') {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.showLoading({ title: '上传中...', mask: true })

    uni.uploadFile({
      url: `${BASE_URL}${url}`,
      filePath,
      name: 'file',
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        uni.hideLoading()
        try {
          const data = JSON.parse(res.data)
          // Handle both wrapped and raw formats
          if (data && typeof data === 'object' && 'data' in data && data.data && data.data.file_url) {
            resolve(data.data.file_url)
          } else if (data && data.file_url) {
            resolve(data.file_url)
          } else {
            resolve(data)
          }
        } catch (e) {
          resolve(res.data)
        }
      },
      fail: (err) => {
        uni.hideLoading()
        uni.showToast({ title: '上传失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

export default {
  get(url, data) {
    return request({ url, method: 'GET', data })
  },
  post(url, data) {
    return request({ url, method: 'POST', data })
  },
  put(url, data) {
    return request({ url, method: 'PUT', data })
  },
  delete(url, data) {
    return request({ url, method: 'DELETE', data })
  },
  upload: uploadFile
}
