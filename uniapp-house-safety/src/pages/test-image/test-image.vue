<template>
  <view class="container">
    <view class="header"><text class="title">检测图片管理</text></view>

    <view v-if="loading" class="loading">加载中...</view>

    <view v-else class="content">
      <view v-for="group in imageGroups" :key="group.type" class="group">
        <text class="group-title">{{ group.label }}</text>
        <view class="image-grid">
          <view v-for="img in group.images" :key="img.id" class="image-item">
            <image :src="img.image_url" mode="aspectFill" class="img" @click="previewImage(img.image_url)" />
            <view class="img-info">
              <text class="img-label">{{ img.label || group.label }}</text>
              <button class="btn-delete" @click="handleDelete(img.id)">×</button>
            </view>
          </view>
          <view class="image-item add-item" @click="handleAdd(group.type)">
            <text class="add-icon">+</text>
            <text class="add-text">添加</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTestImages, createTestImage, deleteTestImage } from '@/api/test-image.js'
import { getSurveyDetail } from '@/api/survey.js'

const surveyId = ref('')
const survey = ref({})
const images = ref([])
const loading = ref(true)

const IMAGE_TYPES = [
  { type: 'elevation_front', label: '正立面' },
  { type: 'elevation_back', label: '背立面' },
  { type: 'floor_plan', label: '平面图' },
  { type: 'site_plan', label: '总平面图' }
]

const imageGroups = computed(() => IMAGE_TYPES.map(t => ({ ...t, images: images.value.filter(img => img.type === t.type) })))

function genLabel(type) {
  const count = images.value.filter(i => i.type === type).length + 1
  const labels = {
    elevation_front: `正立面示意图 ${count}`,
    elevation_back: `背立面示意图 ${count}`,
    floor_plan: survey.value.floorCount ? `一层平面及局部损坏示意图` : `平面图 ${count}`,
    site_plan: `总平面示意图`
  }
  return labels[type] || `${type} ${count}`
}

async function load() {
  try {
    const [imgRes, surveyRes] = await Promise.all([getTestImages(surveyId.value), getSurveyDetail(surveyId.value).catch(() => ({}))])
    images.value = imgRes.items || imgRes || []
    survey.value = surveyRes || {}
  } catch (e) { /* handled */ }
  finally { loading.value = false }
}

async function handleAdd(type) {
  const label = genLabel(type)
  uni.showModal({ title: '添加图片', content: `标签：${label}`, confirmText: '上传', success: async (modalRes) => {
    if (!modalRes.confirm) return
    uni.chooseImage({ count: 1, success: async (res) => {
      try {
        const { default: req } = await import('@/api/request.js')
        const url = await req.upload(res.tempFilePaths[0], '/upload/image')
        const img = await createTestImage(surveyId.value, { type, image_url: url, label, sort_order: images.value.length })
        images.value.push(img)
      } catch (e) { /* handled */ }
    }})
  }})
}

async function handleDelete(id) {
  try {
    await deleteTestImage(surveyId.value, id)
    images.value = images.value.filter(i => i.id !== id)
  } catch (e) { /* handled */ }
}

function previewImage(url) {
  uni.previewImage({ urls: [url] })
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  surveyId.value = currentPage.options.id || ''
  load()
})
</script>

<style scoped>
.container { padding: 20rpx; }
.header { padding: 20rpx 0; }
.title { font-size: 36rpx; font-weight: bold; }
.loading { text-align: center; padding: 100rpx 0; color: #626F7D; }
.group { margin-bottom: 30rpx; }
.group-title { font-size: 30rpx; font-weight: bold; display: block; margin-bottom: 16rpx; }
.image-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.image-item { width: 210rpx; background: #fff; border-radius: 4rpx; overflow: hidden; }
.img { width: 210rpx; height: 210rpx; }
.img-info { padding: 8rpx; display: flex; justify-content: space-between; align-items: center; }
.img-label { font-size: 22rpx; color: #454D59; }
.btn-delete { font-size: 24rpx; color: #D43535; background: none; border: none; padding: 0; line-height: 1; }
.add-item { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 210rpx; border: 2rpx dashed #DBDFE4; }
.add-icon { font-size: 48rpx; color: #DBDFE4; }
.add-text { font-size: 24rpx; color: #626F7D; margin-top: 8rpx; }
</style>
