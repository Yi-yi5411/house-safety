<template>
  <view class="container">
    <view class="header"><text class="title">报告模板管理</text></view>

    <view v-if="loading" class="loading">加载中...</view>

    <view v-else class="content">
      <view v-for="tpl in templates" :key="tpl.id" class="card">
        <view class="card-body">
          <view class="card-info">
            <text class="tpl-name">{{ tpl.name }}</text>
            <text v-if="tpl.is_active" class="active-tag">当前使用</text>
            <text class="tpl-date">{{ formatDate(tpl.created_at) }}</text>
          </view>
          <view class="card-actions">
            <button v-if="!tpl.is_active" class="btn-activate" @click="handleActivate(tpl.id)">启用</button>
            <button class="btn-delete" @click="handleDelete(tpl.id)">删除</button>
          </view>
        </view>
      </view>

      <view v-if="templates.length === 0" class="empty">暂无模板，请上传</view>

      <button class="btn-upload" @click="handleUpload">上传新模板 (.docx)</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReportTemplates, createReportTemplate, setActiveTemplate, deleteReportTemplate } from '@/api/report-template.js'

const templates = ref([])
const loading = ref(true)

async function load() {
  try {
    const result = await getReportTemplates()
    templates.value = result.items || result || []
  } catch (e) { /* handled */ }
  finally { loading.value = false }
}

async function handleUpload() {
  // In mini-program, use uni.chooseMessageFile for .docx
  // #ifdef MP-WEIXIN
  uni.chooseMessageFile({
    count: 1,
    type: 'file',
    extension: ['.docx'],
    success: async (res) => {
      const file = res.tempFiles[0]
      try {
        const { default: req } = await import('@/api/request.js')
        const url = await req.upload(file.path, '/upload/file')
        const tpl = await createReportTemplate({ name: file.name, file_path: url })
        templates.value.push(tpl)
      } catch (e) { /* handled */ }
    }
  })
  // #endif
  // #ifndef MP-WEIXIN
  uni.showToast({ title: '请在小程序中使用', icon: 'none' })
  // #endif
}

async function handleActivate(id) {
  try {
    await setActiveTemplate(id)
    templates.value.forEach(t => { t.is_active = (t.id === id) })
  } catch (e) { /* handled */ }
}

async function handleDelete(id) {
  try {
    await deleteReportTemplate(id)
    templates.value = templates.value.filter(t => t.id !== id)
  } catch (e) { /* handled */ }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.substring(0, 10)
}

onMounted(load)
</script>

<style scoped>
.container { padding: 20rpx; }
.header { padding: 20rpx 0; }
.title { font-size: 36rpx; font-weight: bold; }
.loading { text-align: center; padding: 100rpx 0; color: #626F7D; }
.card { background: #fff; border-radius: 4rpx; padding: 24rpx; margin-bottom: 16rpx; }
.card-body { display: flex; justify-content: space-between; align-items: center; }
.card-info { flex: 1; }
.tpl-name { font-size: 30rpx; font-weight: bold; display: block; }
.active-tag { font-size: 22rpx; color: #2EA65E; background: #f6ffed; padding: 2rpx 8rpx; border-radius: 4rpx; }
.tpl-date { font-size: 24rpx; color: #626F7D; display: block; margin-top: 4rpx; }
.card-actions { display: flex; gap: 12rpx; }
.btn-activate { font-size: 24rpx; padding: 8rpx 16rpx; background: #226CB3; color: #fff; border-radius: 6rpx; border: none; }
.btn-delete { font-size: 24rpx; padding: 8rpx 16rpx; background: none; color: #D43535; border: 1rpx solid #D43535; border-radius: 6rpx; }
.btn-upload { background: #226CB3; color: #fff; border-radius: 4rpx; margin-top: 30rpx; }
.empty { text-align: center; padding: 100rpx 0; color: #626F7D; }
</style>
