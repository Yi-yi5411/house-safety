<template>
  <view class="container">
    <view class="header">
      <text class="title">原始记录</text>
    </view>

    <view v-if="loading" class="loading">加载中...</view>

    <view v-else class="content">
      <!-- Survey Info -->
      <view class="section">
        <text class="section-title">基本信息</text>
        <view class="info-row"><text class="label">地址：</text><text>{{ record.survey?.address || 'N/A' }}</text></view>
        <view class="info-row"><text class="label">结构类型：</text><text>{{ record.survey?.structure_type || 'N/A' }}</text></view>
        <view class="info-row"><text class="label">建造年份：</text><text>{{ record.survey?.build_year || 'N/A' }}</text></view>
        <view class="info-row"><text class="label">鉴定结论：</text><text class="conclusion">{{ record.survey?.conclusion || '待评定' }}</text></view>
      </view>

      <!-- Components -->
      <view class="section">
        <text class="section-title">构件检查记录</text>
        <view v-for="c in record.components" :key="c.id" class="card">
          <text class="comp-name">{{ c.name }} <text class="comp-cat">({{ c.category }})</text></text>
          <view class="info-row" v-if="c.axis_line || c.axisLine"><text class="label">轴线位置：</text><text>{{ c.axis_line || c.axisLine }}</text></view>
          <view class="info-row" v-if="c.ai_evaluation_result || c.aiEvaluationResult"><text class="label">评定结果：</text><text class="result-text">{{ c.ai_evaluation_result || c.aiEvaluationResult }}</text><text v-if="c.ai_evaluation_clause || c.aiEvaluationClause" class="clause"> ({{ c.ai_evaluation_clause || c.aiEvaluationClause }})</text></view>
          <view class="info-row"><text class="label">损坏等级：</text><text>{{ getLevelText(c.damage_level || c.damageLevel) || '-' }}</text></view>
          <view class="info-row"><text class="label">损坏描述：</text><text>{{ c.damage_description || c.damage_desc || c.damageDesc || '-' }}</text></view>
          <!-- 已勾选标准 -->
          <view v-if="(c.checked_item_ids || c.checkedItemIds || []).length > 0" class="checked-box">
            <text class="checked-title">已勾选标准：</text>
            <view v-for="sid in (c.checked_item_ids || c.checkedItemIds || [])" :key="sid" class="checked-line">
              <text class="dot">•</text>
              <text class="desc">{{ getStdDesc(sid) }}</text>
              <text v-if="getStdResult(sid)" class="badge" :style="{ background: getColor(getStdResult(sid)) }">{{ getStdResult(sid) }}</text>
            </view>
          </view>
          <!-- 照片 -->
          <view v-if="c.photos && c.photos.length > 0" class="photos">
            <image v-for="(p, pi) in c.photos" :key="pi" :src="p" class="photo" mode="aspectFill" @click="previewImg(p, c.photos)" />
          </view>
        </view>
        <view v-if="!record.components || record.components.length === 0" class="empty">暂无构件检查记录</view>
      </view>

      <button class="btn-export" @click="handleExport">导出原始记录 (.docx)</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOriginalRecord, exportOriginalRecord } from '@/api/survey.js'
import { getEvaluationStandards } from '@/api/damage-component.js'

const surveyId = ref('')
const record = ref({ survey: null, components: [] })
const loading = ref(true)
const stdfull = ref([])

const getLevelText = (l) => ({ minor: '轻微', moderate: '中等', severe: '严重', dangerous: '危险' }[l] || '')
const getColor = (r) => ({ '完好': '#2EA65E', '基本完好': '#226CB3', '一般损坏': '#E28A13', '严重损坏': '#D43535', '危险': '#D43535', '危险状态': '#D43535' }[r] || '#626F7D')
const getStdDesc = (id) => { const s = stdfull.value.find(x => x.id === id); return s ? s.description || '' : '' }
const getStdResult = (id) => { const s = stdfull.value.find(x => x.id === id); return s ? s.evaluationResult || s.evaluation_result || '' : '' }
const previewImg = (url, list) => uni.previewImage({ current: url, urls: list })

async function load() {
  try {
    const [recData, stdData] = await Promise.all([getOriginalRecord(surveyId.value), getEvaluationStandards()])
    record.value = recData
    stdfull.value = stdData.items || stdData || []
  } catch (e) { /* handled */ }
  finally { loading.value = false }
}

async function handleExport() {
  try {
    const filePath = await exportOriginalRecord(surveyId.value)
    uni.showToast({ title: '导出成功', icon: 'success' })
    // Open the file
    uni.openDocument({ filePath, showMenu: true })
  } catch (e) {
    uni.showToast({ title: '导出失败', icon: 'none' })
  }
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
.section { margin-bottom: 30rpx; }
.section-title { font-size: 30rpx; font-weight: bold; display: block; margin-bottom: 16rpx; color: #226CB3; }
.info-row { font-size: 28rpx; color: #171D26; margin-bottom: 8rpx; }
.label { color: #454D59; }
.conclusion { color: #D43535; font-weight: bold; }
.card { background: #fff; border-radius: 4rpx; padding: 20rpx; margin-bottom: 16rpx; }
.comp-name { font-size: 28rpx; font-weight: bold; display: block; margin-bottom: 8rpx; }
.comp-cat { font-weight: normal; color: #626F7D; font-size: 24rpx; }
.btn-export { background: #226CB3; color: #fff; border-radius: 4rpx; margin-top: 30rpx; }
.empty { text-align: center; padding: 40rpx 0; color: #626F7D; }
</style>
