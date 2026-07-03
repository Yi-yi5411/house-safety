<template>
  <view class="ai-chat">
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
        </view>
      </view>
    </scroll-view>
    
    <view class="input-bar">
      <input 
        v-model="inputText" 
        placeholder="输入问题..." 
        class="chat-input"
        @confirm="handleSend"
      />
      <button class="btn-send" @click="handleSend">发送</button>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  surveyId: {
    type: String,
    required: true
  }
})

const messages = ref([])
const inputText = ref('')
const scrollToView = ref('')

const handleSend = async () => {
  if (!inputText.value.trim()) return
  
  messages.value.push({
    role: 'user',
    content: inputText.value
  })
  
  const question = inputText.value
  inputText.value = ''
  await scrollToBottom()
  
  // 模拟AI回复
  setTimeout(() => {
    messages.value.push({
      role: 'ai',
      content: `关于"${question}"，建议您参考相关鉴定标准进行评定。`
    })
    scrollToBottom()
  }, 1000)
}

const scrollToBottom = async () => {
  await nextTick()
  scrollToView.value = `msg-${messages.value.length - 1}`
}
</script>

<style scoped>
.ai-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-container {
  flex: 1;
  padding: 20rpx;
}

.message-item {
  display: flex;
  margin-bottom: 24rpx;
}

.message-user {
  flex-direction: row-reverse;
}

.message-ai {
  flex-direction: row;
}

.message-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  color: #ffffff;
  flex-shrink: 0;
}

.message-user .message-avatar {
  background-color: #226CB3;
  margin-left: 16rpx;
}

.message-ai .message-avatar {
  background-color: #2EA65E;
  margin-right: 16rpx;
}

.message-content {
  max-width: 70%;
  padding: 16rpx;
  border-radius: 4rpx;
  background-color: #ffffff;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.02);
}

.message-user .message-content {
  background-color: #226CB3;
  color: #ffffff;
}

.message-text {
  font-size: 26rpx;
  line-height: 1.5;
  word-break: break-all;
}

.input-bar {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background-color: #ffffff;
  border-top: 1rpx solid #DBDFE4;
}

.chat-input {
  flex: 1;
  height: 64rpx;
  padding: 0 20rpx;
  background-color: #EDF0F4;
  border-radius: 6rpx;
  font-size: 26rpx;
}

.btn-send {
  margin-left: 16rpx;
  background-color: #226CB3;
  color: #ffffff;
  border: none;
  border-radius: 6rpx;
  padding: 14rpx 28rpx;
  font-size: 26rpx;
}
</style>
