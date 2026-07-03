import request from './request.js'

// 发送手机验证码
export function sendPhoneCode(phone) {
  return request.post('/auth/phone/send', { phone })
}

// 手机号+验证码登录
export function phoneLogin(phone, code) {
  return request.post('/auth/login/phone', { phone, code })
}

// 微信小程序登录
export function wechatLogin(code) {
  return request.post('/auth/wechat/login', { code })
}

// 发送邮箱验证码
export function sendEmailCode(email) {
  return request.post('/auth/email/send', { email })
}

// 邮箱+验证码登录
export function emailLogin(email, code) {
  return request.post('/auth/login/email', { email, code })
}

// 获取当前用户信息
export function getCurrentUser() {
  return request.get('/auth/me')
}

// 注册
export function register(email, code, nickname) {
  return request.post('/auth/register', { email, code, nickname })
}
