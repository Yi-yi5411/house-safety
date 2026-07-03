<template>
  <view class="survey-card" @click="handleClick">
    <view class="card-header">
      <text class="card-title">{{ survey.address || '未命名项目' }}</text>
      <view class="status-badge" :class="`status-${survey.status}`">
        {{ getStatusText(survey.status) }}
      </view>
    </view>
    <view class="card-body">
      <view class="info-row">
        <text class="info-label">结构类型</text>
        <text class="info-value">{{ survey.structure_type || survey.structureType || '-' }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">建造年代</text>
        <text class="info-value">{{ survey.build_year || survey.buildYear || '-' }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">鉴定时间</text>
        <text class="info-value">{{ survey.survey_time || survey.surveyTime || '-' }}</text>
      </view>
      <view v-if="survey.conclusion" class="info-row">
        <text class="info-label">鉴定结论</text>
        <text class="conclusion-badge" :class="`level-${survey.conclusion}`">
          {{ survey.conclusion }}级
        </text>
      </view>
    </view>
    <view class="card-footer">
      <text class="card-time">{{ formatTime(survey.created_at || survey.createdAt) }}</text>
      <view class="card-actions">
        <button class="btn-action btn-view" size="mini" @click.stop="handleView">查看</button>
        <button class="btn-action btn-delete" size="mini" @click.stop="handleDelete">删除</button>
      </view>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({
  survey: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'delete'])

const handleClick = () => {
  emit('click', props.survey)
}

const handleView = () => {
  emit('click', props.survey)
}

const handleDelete = () => {
  emit('delete', props.survey)
}

const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    completed: '已完成',
    exported: '已导出'
  }
  return map[status] || status
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>

<style scoped>
.survey-card {
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
  margin-bottom: 16rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #DBDFE4;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #171D26;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 6rpx;
  color: #ffffff;
  margin-left: 16rpx;
}

.status-draft { background-color: #626F7D; }
.status-completed { background-color: #2EA65E; }
.status-exported { background-color: #226CB3; }

.card-body {
  margin-bottom: 16rpx;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 8rpx 0;
}

.info-label {
  width: 140rpx;
  font-size: 26rpx;
  color: #626F7D;
}

.info-value {
  flex: 1;
  font-size: 26rpx;
  color: #454D59;
}

.conclusion-badge {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
  color: #ffffff;
}

.level-A { background-color: #2EA65E; }
.level-B { background-color: #E28A13; }
.level-C { background-color: #E28A13; }
.level-D { background-color: #D43535; }

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16rpx;
  border-top: 1rpx solid #DBDFE4;
}

.card-time {
  font-size: 24rpx;
  color: #626F7D;
}

.card-actions {
  display: flex;
  gap: 16rpx;
}

.btn-action {
  border: none;
  border-radius: 4rpx;
  padding: 12rpx 24rpx;
  font-size: 24rpx;
}

.btn-view {
  background-color: #226CB3;
  color: #ffffff;
}

.btn-delete {
  background-color: #D43535;
  color: #ffffff;
}
</style>
