<template>
  <view class="container">
    <!-- 当前鉴定上下文 -->
    <view class="context-bar" v-if="surveyContext">
      <view class="context-header">
        <text class="context-title">当前鉴定：{{ surveyContext.address || '-' }}</text>
        <button class="btn-save" size="mini" @click="handleSaveResult">保存推理结果</button>
      </view>
      <view class="context-meta" v-if="surveyContext.conclusion">
        <text class="context-badge" :style="{ background: getLevelColor(surveyContext.conclusion) }">{{ surveyContext.conclusion }}级</text>
        <text class="context-text">{{ surveyContext.basicEvaluation || '' }}</text>
      </view>
    </view>
    <!-- 聊天消息列表 -->
    <scroll-view 
      scroll-y 
      class="chat-container" 
      :scroll-into-view="scrollToView"
      scroll-with-animation
    >
      <view 
        v-for="(msg, index) in messages" 
        :key="index" 
        :id="`msg-${index}`"
        class="message-item"
        :class="msg.role === 'user' ? 'message-user' : 'message-ai'"
      >
        <view class="message-avatar">
          <text v-if="msg.role === 'user'">我</text>
          <text v-else>AI</text>
        </view>
        <view class="message-content">
          <text class="message-text">{{ msg.content }}</text>
          <text class="message-time">{{ msg.time }}</text>
        </view>
      </view>
      
      <!-- AI正在输入 -->
      <view v-if="aiTyping" class="message-item message-ai">
        <view class="message-avatar">
          <text>AI</text>
        </view>
        <view class="message-content">
          <view class="typing-indicator">
            <view class="typing-dot"></view>
            <view class="typing-dot"></view>
            <view class="typing-dot"></view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 快捷问题 -->
    <view v-if="messages.length <= 1" class="quick-questions">
      <text class="quick-title">快捷问题</text>
      <view class="quick-list">
        <button 
          v-for="q in quickQuestions" 
          :key="q"
          class="quick-btn" 
          size="mini"
          @click="handleQuickQuestion(q)"
        >
          {{ q }}
        </button>
      </view>
    </view>

    <!-- 输入框 -->
    <view class="input-bar">
      <input 
        v-model="inputText" 
        placeholder="输入您的问题..." 
        class="chat-input"
        @confirm="handleSend"
      />
      <button class="btn-send" @click="handleSend">发送</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { aiAssistantChat } from '@/api/ai.js'
import { getSurveyDetail, updateSurvey } from '@/api/survey.js'

const surveyId = ref('')
const surveyContext = ref(null)
const conversationId = ref('')
const messages = ref([])
const inputText = ref('')
const aiTyping = ref(false)
const scrollToView = ref('')

const quickQuestions = [
  '请根据检测数据给出鉴定结论',
  '损坏构件的评定是否准确？',
  '报告内容有哪些需要补充？',
  '给出处理建议'
]

const getLevelColor = (l) => ({ A: '#2EA65E', B: '#226CB3', C: '#E28A13', D: '#D43535' }[l] || '#626F7D')

onMounted(async () => {
  const pages = getCurrentPages(); const cp = pages[pages.length - 1]
  surveyId.value = cp.options.id || ''
  try {
    surveyContext.value = await getSurveyDetail(surveyId.value)
  } catch (e) { /* ignore */ }
  messages.value.push({ role: 'ai', content: '您好！我是AI助手，可以为您分析鉴定数据、提供专业建议。请问有什么可以帮助您的？', time: getCurrentTime() })
})

const handleSend = async () => {
  if (!inputText.value.trim()) return
  const userMessage = { role: 'user', content: inputText.value, time: getCurrentTime() }
  messages.value.push(userMessage)
  const question = inputText.value
  inputText.value = ''
  await scrollToBottom()
  aiTyping.value = true; await scrollToBottom()
  try {
    // Send survey context with the query for better answers
    const ctx = surveyContext.value ? `[当前鉴定数据: 地址=${surveyContext.value.address}, 结构=${surveyContext.value.structureType}, 层数=${surveyContext.value.floorCount}, 面积=${surveyContext.value.buildArea}㎡, 结论=${surveyContext.value.conclusion || '未评定'}] ` : ''
    const res = await aiAssistantChat(conversationId.value, ctx + question, '')
    aiTyping.value = false
    if (res.conversation_id) conversationId.value = res.conversation_id
    messages.value.push({ role: 'ai', content: res.content || '抱歉，我暂时无法回答这个问题。', time: getCurrentTime() })
    await scrollToBottom()
  } catch (error) {
    aiTyping.value = false
    messages.value.push({ role: 'ai', content: '抱歉，服务暂时不可用，请稍后重试。', time: getCurrentTime() })
  }
}

const handleSaveResult = async () => {
  if (!surveyId.value) return
  try {
    // Extract conclusion/risk info from last AI message
    const lastAi = [...messages.value].reverse().find(m => m.role === 'ai')
    if (!lastAi) return uni.showToast({ title: '暂无AI回复可保存', icon: 'none' })
    await updateSurvey(surveyId.value, { aiReasoningResult: { rawResponse: lastAi.content, savedAt: new Date().toISOString() } })
    uni.showToast({ title: '已保存推理结果', icon: 'success' })
  } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
}

const handleQuickQuestion = (question) => {
  inputText.value = question
  handleSend()
}

const scrollToBottom = async () => {
  await nextTick()
  scrollToView.value = `msg-${messages.value.length - 1}`
}

const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #F5F7FA;
}

.chat-container {
  flex: 1;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.message-item {
  display: flex;
  margin-bottom: 30rpx;
}

.message-user {
  flex-direction: row-reverse;
}

.message-ai {
  flex-direction: row;
}

.message-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #ffffff;
  flex-shrink: 0;
}

.message-user .message-avatar {
  background-color: #226CB3;
  margin-left: 20rpx;
}

.message-ai .message-avatar {
  background-color: #2EA65E;
  margin-right: 20rpx;
}

.message-content {
  max-width: 70%;
  padding: 20rpx;
  border-radius: 4rpx;
  background-color: #ffffff;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.02);
}

.message-user .message-content {
  background-color: #226CB3;
  color: #ffffff;
}

.message-text {
  font-size: 28rpx;
  line-height: 1.6;
  word-break: break-all;
}

.message-time {
  display: block;
  font-size: 20rpx;
  color: #626F7D;
  margin-top: 8rpx;
  text-align: right;
}

.message-user .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.typing-indicator {
  display: flex;
  gap: 12rpx;
  padding: 10rpx 0;
}

.typing-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background-color: #626F7D;
  animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10rpx);
    opacity: 1;
  }
}

.quick-questions {
  padding: 20rpx;
  background-color: #ffffff;
  border-radius: 4rpx;
  margin: 0 20rpx 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.02);
}

.quick-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #171D26;
  margin-bottom: 16rpx;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.quick-btn {
  background-color: #E8F0F8;
  color: #226CB3;
  border: 1rpx solid #226CB3;
  border-radius: 6rpx;
  padding: 12rpx 24rpx;
  font-size: 24rpx;
}

.input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  padding: 20rpx;
  background-color: #ffffff;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.chat-input {
  flex: 1;
  height: 72rpx;
  padding: 0 24rpx;
  background-color: #EDF0F4;
  border-radius: 6rpx;
  font-size: 28rpx;
}

.btn-send {
  margin-left: 20rpx;
  background-color: #226CB3;
  color: #ffffff;
  border: none;
  border-radius: 6rpx;
  padding: 16rpx 32rpx;
  font-size: 28rpx;
}
</style>
