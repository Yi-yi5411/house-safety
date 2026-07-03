<template>
  <view class="container">
    <view class="header">
      <text class="title">签字盖章管理</text>
    </view>

    <view v-if="loading" class="loading">加载中...</view>

    <view v-else class="content">
      <view v-for="sig in signatures" :key="sig.id" class="card">
        <view class="card-header">
          <text class="type-label">{{ typeLabel(sig.type) }}</text>
          <button class="btn-delete" @click="handleDelete(sig.id)">删除</button>
        </view>
        <view class="form-row">
          <text class="label">签署人姓名</text>
          <input v-model="sig.signatory_name" placeholder="请输入姓名" @blur="handleUpdate(sig)" />
        </view>
        <view class="form-row">
          <text class="label">签署日期</text>
          <picker mode="date" :value="sig.sign_date" @change="(e) => handleDateChange(sig, e)">
            <text>{{ sig.sign_date || '请选择日期' }}</text>
          </picker>
        </view>
        <view class="form-row">
          <text class="label">签名图片</text>
          <button class="btn-upload" @click="handleUploadImage(sig)">上传图片</button>
          <image v-if="sig.image_url" :src="sig.image_url" mode="widthFix" class="preview-img" />
        </view>
      </view>

      <button class="btn-add" @click="handleAdd">+ 新增签字盖章</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSignatures, createSignature, updateSignature, deleteSignature } from '@/api/signature.js'

const surveyId = ref('')
const signatures = ref([])
const loading = ref(true)

const SIGNATURE_TYPES = [
  { value: 'appraiser', label: '鉴定人' },
  { value: 'reviewer', label: '审核人' },
  { value: 'issuer', label: '签发人' },
  { value: 'seal', label: '单位公章' }
]

function typeLabel(type) {
  const found = SIGNATURE_TYPES.find(t => t.value === type)
  return found ? found.label : type
}

async function loadSignatures() {
  try {
    const result = await getSignatures(surveyId.value)
    signatures.value = result.items || result || []
  } catch (e) { /* handled by request */ }
  finally { loading.value = false }
}

async function handleAdd() {
  const type = SIGNATURE_TYPES[signatures.value.length % SIGNATURE_TYPES.length].value
  try {
    const sig = await createSignature(surveyId.value, { type })
    signatures.value.push(sig)
  } catch (e) { /* handled */ }
}

async function handleUpdate(sig) {
  try {
    await updateSignature(surveyId.value, sig.id, {
      signatory_name: sig.signatory_name,
      image_url: sig.image_url,
      sign_date: sig.sign_date
    })
  } catch (e) { /* handled */ }
}

function handleDateChange(sig, e) {
  sig.sign_date = e.detail.value
  handleUpdate(sig)
}

async function handleDelete(id) {
  try {
    await deleteSignature(surveyId.value, id)
    signatures.value = signatures.value.filter(s => s.id !== id)
  } catch (e) { /* handled */ }
}

async function handleUploadImage(sig) {
  uni.chooseImage({
    count: 1,
    success: async (res) => {
      const filePath = res.tempFilePaths[0]
      try {
        const { default: req } = await import('@/api/request.js')
        const url = await req.upload(filePath, '/upload/image')
        sig.image_url = url
        await handleUpdate(sig)
      } catch (e) { /* handled */ }
    }
  })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  surveyId.value = currentPage.options.id || ''
  loadSignatures()
})
</script>

<style scoped>
.container { padding: 20rpx; }
.header { padding: 20rpx 0; }
.title { font-size: 36rpx; font-weight: bold; }
.loading { text-align: center; padding: 100rpx 0; color: #626F7D; }
.card { background: #fff; border-radius: 6rpx; padding: 24rpx; margin-bottom: 20rpx; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.type-label { font-size: 30rpx; font-weight: bold; color: #226CB3; }
.btn-delete { font-size: 24rpx; color: #D43535; background: none; border: none; padding: 0; }
.form-row { margin-bottom: 16rpx; }
.label { font-size: 26rpx; color: #454D59; display: block; margin-bottom: 8rpx; }
.form-row input { border: 1rpx solid #E5E8EC; border-radius: 4rpx; padding: 12rpx; font-size: 28rpx; width: 100%; box-sizing: border-box; }
.btn-upload { font-size: 24rpx; margin-bottom: 8rpx; }
.preview-img { width: 200rpx; margin-top: 8rpx; border-radius: 4rpx; }
.btn-add { background: #226CB3; color: #fff; border-radius: 4rpx; margin-top: 20rpx; }
</style>
