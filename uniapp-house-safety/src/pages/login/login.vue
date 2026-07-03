<template>
  <view class="login-container">
    <!-- Logo 和标题 -->
    <view class="header">
      <image class="logo" src="/static/logo.png" mode="aspectFit" />
      <text class="title">房屋安全鉴定系统</text>
      <text class="subtitle">专业 · 高效 · 智能</text>
    </view>

    <!-- 登录表单 -->
    <view class="login-form">
      <!-- 手机号登录 -->
      <view class="form-item">
        <input 
          v-model="phoneNumber" 
          type="number" 
          placeholder="请输入手机号" 
          class="input"
          maxlength="11"
        />
      </view>
      <view class="form-item">
        <input 
          v-model="verifyCode" 
          type="number" 
          placeholder="请输入验证码" 
          class="input"
          maxlength="6"
        />
        <button 
          class="btn-code" 
          :disabled="codeSending" 
          @click="handleSendCode"
        >
          {{ codeSending ? `${countdown}s` : '获取验证码' }}
        </button>
      </view>
      <button class="btn-login" @click="handlePhoneLogin">手机号登录</button>

      <!-- 分隔线 -->
      <view class="divider">
        <view class="divider-line"></view>
        <text class="divider-text">或</text>
        <view class="divider-line"></view>
      </view>

      <!-- 微信登录 -->
      <button class="btn-wechat" @click="handleWechatLogin">
        <image class="wechat-icon" src="/static/wechat-icon.png" mode="aspectFit" />
        微信一键登录
      </button>
    </view>

    <!-- 用户协议 -->
    <view class="agreement">
      <checkbox-group @change="handleAgreementChange">
        <label class="agreement-label">
          <checkbox :checked="agreed" color="#226CB3" />
          <text class="agreement-text">
            我已阅读并同意
            <text class="link">《用户服务协议》</text>
            和
            <text class="link">《隐私政策》</text>
          </text>
        </label>
      </checkbox-group>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { sendPhoneCode, phoneLogin, wechatLogin } from '@/api/auth.js'
import { setLoginStatus, setUserInfo, setToken } from '@/utils/auth.js'

const phoneNumber = ref('')
const verifyCode = ref('')
const codeSending = ref(false)
const countdown = ref(60)
const agreed = ref(false)

const handleSendCode = async () => {
  if (!phoneNumber.value || phoneNumber.value.length !== 11) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  
  codeSending.value = true
  try {
    await sendPhoneCode(phoneNumber.value)
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    
    // 开始倒计时
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
        codeSending.value = false
        countdown.value = 60
      }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
    uni.showToast({ title: '发送失败', icon: 'none' })
    codeSending.value = false
  }
}

const handlePhoneLogin = async () => {
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议', icon: 'none' })
    return
  }
  
  if (!phoneNumber.value || !verifyCode.value) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' })
    return
  }
  
  try {
    const res = await phoneLogin(phoneNumber.value, verifyCode.value)

    if (res.access_token) {
      setToken(res.access_token)
      setLoginStatus(true)
      setUserInfo({ phone: phoneNumber.value })
      uni.showToast({ title: '登录成功', icon: 'success' })
      setTimeout(() => {
        uni.switchTab({ url: '/pages/index/index' })
      }, 1000)
    }
  } catch (error) {
    console.error('手机号登录失败:', error)
    uni.showToast({ title: '登录失败', icon: 'none' })
  }
}

const handleWechatLogin = async () => {
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议', icon: 'none' })
    return
  }
  
  try {
    // 获取微信登录 code (uni.login uses callback, wrap in Promise)
    const loginRes = await new Promise((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: resolve,
        fail: reject
      })
    })

    if (loginRes.code) {
      const res = await wechatLogin(loginRes.code)

      if (res.access_token) {
        setToken(res.access_token)
        setLoginStatus(true)
        setUserInfo({ wechat: true })
        uni.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/index/index' })
        }, 1000)
      }
    }
  } catch (error) {
    console.error('微信登录失败:', error)
    uni.showToast({ title: '微信登录失败，请重试', icon: 'none' })
  }
}

const handleAgreementChange = (e) => {
  agreed.value = e.detail.value.length > 0
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #226CB3 0%, #1B5A96 100%);
  padding: 100rpx 60rpx;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 80rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 30rpx;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.login-form {
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.form-item {
  margin-bottom: 30rpx;
  display: flex;
  align-items: center;
}

.input {
  flex: 1;
  height: 80rpx;
  padding: 0 24rpx;
  background-color: #EDF0F4;
  border-radius: 4rpx;
  font-size: 28rpx;
}

.btn-code {
  margin-left: 20rpx;
  background-color: #226CB3;
  color: #ffffff;
  border: none;
  border-radius: 4rpx;
  padding: 20rpx 30rpx;
  font-size: 24rpx;
  white-space: nowrap;
}

.btn-code[disabled] {
  background-color: #A3C5E8;
}

.btn-login {
  background-color: #226CB3;
  color: #ffffff;
  border: none;
  border-radius: 4rpx;
  padding: 24rpx 0;
  font-size: 32rpx;
  margin-top: 20rpx;
}

.divider {
  display: flex;
  align-items: center;
  margin: 40rpx 0;
}

.divider-line {
  flex: 1;
  height: 2rpx;
  background-color: #DBDFE4;
}

.divider-text {
  margin: 0 20rpx;
  color: #626F7D;
  font-size: 24rpx;
}

.btn-wechat {
  background-color: #2EA65E;
  color: #ffffff;
  border: none;
  border-radius: 4rpx;
  padding: 24rpx 0;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wechat-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 16rpx;
}

.agreement {
  margin-top: 40rpx;
  text-align: center;
}

.agreement-label {
  display: flex;
  align-items: center;
  justify-content: center;
}

.agreement-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 10rpx;
}

.link {
  color: #ffffff;
  text-decoration: underline;
}
</style>
