<template>
  <view class="container">
    <!-- 基本信息 -->
    <view class="card">
      <view class="card-header">
        <text class="card-title">基本信息</text>
        <button class="btn-edit" size="mini" @click="handleEdit">编辑</button>
      </view>
      <view class="info-list">
        <view class="info-item">
          <text class="info-label">房屋地址</text>
          <text class="info-value">{{ survey.address || '未填写' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">建造年代</text>
          <text class="info-value">{{ survey.build_year || survey.buildYear || '未填写' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">结构类型</text>
          <text class="info-value">{{ survey.structure_type || survey.structureType || '未填写' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">楼层数</text>
          <text class="info-value">{{ survey.floor_count || survey.floorCount ? `${survey.floor_count || survey.floorCount}层` : '未填写' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">建筑面积</text>
          <text class="info-value">{{ survey.build_area || survey.buildArea ? `${survey.build_area || survey.buildArea}㎡` : '未填写' }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">鉴定时间</text>
          <text class="info-value">{{ survey.survey_time || survey.surveyTime || '未填写' }}</text>
        </view>
      </view>
    </view>

    <!-- 鉴定结论 -->
    <view v-if="survey.conclusion" class="card">
      <view class="card-header">
        <text class="card-title">鉴定结论</text>
      </view>
      <view class="conclusion-box" :class="`level-${survey.conclusion}`">
        <text class="conclusion-level">{{ survey.conclusion }}级</text>
        <text class="conclusion-text">{{ survey.basic_evaluation || survey.basicEvaluation }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="btn-action btn-data" @click="goToDataCollection">数据采集</button>
      <button class="btn-action btn-damage" @click="goToDamageRecord">损坏记录</button>
      <button class="btn-action btn-report" @click="goToReportPreview">报告预览</button>
      <button class="btn-action btn-ai" @click="goToAiAssistant">AI助手</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSurveyDetail } from '@/api/survey.js'

const surveyId = ref('')
const survey = ref({})

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  surveyId.value = currentPage.options.id || ''
  loadSurveyDetail()
})

const loadSurveyDetail = async () => {
  try {
    const res = await getSurveyDetail(surveyId.value)
    survey.value = res
  } catch (error) {
    console.error('加载鉴定详情失败:', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const handleEdit = () => {
  uni.navigateTo({
    url: `/pages/data-collection/data-collection?id=${surveyId.value}&edit=true`
  })
}

const goToDataCollection = () => {
  uni.navigateTo({
    url: `/pages/data-collection/data-collection?id=${surveyId.value}`
  })
}

const goToDamageRecord = () => {
  uni.navigateTo({
    url: `/pages/damage-record/damage-record?id=${surveyId.value}`
  })
}

const goToReportPreview = () => {
  uni.navigateTo({
    url: `/pages/report-preview/report-preview?id=${surveyId.value}`
  })
}

const goToAiAssistant = () => {
  uni.navigateTo({
    url: `/pages/ai-assistant/ai-assistant?id=${surveyId.value}`
  })
}
</script>

<style scoped>
.container {
  padding: 20rpx;
  padding-bottom: 40rpx;
}

.card {
  background-color: #ffffff;
  border-radius: 4rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.02);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #DBDFE4;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #171D26;
}

.btn-edit {
  background-color: #226CB3;
  color: #ffffff;
  border: none;
  border-radius: 4rpx;
  padding: 12rpx 24rpx;
  font-size: 24rpx;
}

.info-list {
  padding: 10rpx 0;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx dashed #DBDFE4;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  width: 160rpx;
  font-size: 28rpx;
  color: #626F7D;
}

.info-value {
  flex: 1;
  font-size: 28rpx;
  color: #171D26;
}

.conclusion-box {
  padding: 24rpx;
  border-radius: 4rpx;
  background-color: #E8F0F8;
}

.level-A {
  background-color: #E8F0F8;
  border-left: 8rpx solid #2EA65E;
}

.level-B {
  background-color: #FBF0E0;
  border-left: 8rpx solid #E28A13;
}

.level-C {
  background-color: #FAEAEA;
  border-left: 8rpx solid #E28A13;
}

.level-D {
  background-color: #FAEAEA;
  border-left: 8rpx solid #D43535;
}

.conclusion-level {
  font-size: 48rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
}

.level-A .conclusion-level { color: #2EA65E; }
.level-B .conclusion-level { color: #E28A13; }
.level-C .conclusion-level { color: #E28A13; }
.level-D .conclusion-level { color: #D43535; }

.conclusion-text {
  font-size: 26rpx;
  color: #454D59;
  line-height: 1.6;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
  margin-top: 20rpx;
}

.btn-action {
  border: none;
  border-radius: 4rpx;
  padding: 24rpx 0;
  font-size: 28rpx;
  color: #ffffff;
}

.btn-data { background-color: #226CB3; }
.btn-damage { background-color: #2EA65E; }
.btn-report { background-color: #E28A13; }
.btn-ai { background-color: #626F7D; }
</style>
