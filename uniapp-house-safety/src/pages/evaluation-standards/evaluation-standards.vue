<template>
  <view class="container">
    <view class="header"><text class="title">评定标准库</text></view>

    <view class="filters">
      <picker mode="selector" :range="categories" @change="onCategoryChange">
        <text class="filter-btn">{{ selectedCategory || '全部类别' }}</text>
      </picker>
      <picker v-if="selectedCategory" mode="selector" :range="componentTypes" @change="onComponentTypeChange">
        <text class="filter-btn">{{ selectedComponentType || '全部构件类型' }}</text>
      </picker>
    </view>

    <view v-if="loading" class="loading">加载中...</view>

    <view v-else class="list">
      <view v-for="item in standards" :key="item.id" class="card">
        <view class="card-row">
          <text class="badge">{{ item.category }}</text>
          <text class="badge badge-type">{{ item.component_type }}</text>
        </view>
        <text class="desc">{{ item.description }}</text>
        <view class="result-row">
          <text class="result">{{ item.evaluation_result }}</text>
          <text v-if="item.evaluation_clause" class="clause">{{ item.evaluation_clause }}</text>
        </view>
      </view>

      <view v-if="standards.length === 0" class="empty">暂无数据</view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getEvaluationStandards } from '@/api/damage-component.js'

const standards = ref([])
const loading = ref(true)

const categories = ['', '地基基础', '上部承重结构', '围护结构', '其他']
const selectedCategory = ref('')
const componentTypes = ref([])
const selectedComponentType = ref('')

async function load() {
  loading.value = true
  try {
    const params = {}
    if (selectedCategory.value) params.category = selectedCategory.value
    if (selectedComponentType.value) params.componentType = selectedComponentType.value
    const result = await getEvaluationStandards(params)
    standards.value = result.items || result || []

    // Populate componentTypes from results when no component_type filter is active
    if (!selectedComponentType.value && standards.value.length > 0) {
      const types = [...new Set(standards.value.map(s => s.component_type || s.componentType).filter(Boolean))]
      componentTypes.value = ['', ...types]
    }
  } catch (e) { /* handled */ }
  finally { loading.value = false }
}

function onCategoryChange(e) {
  selectedCategory.value = categories[e.detail.value] || ''
  selectedComponentType.value = ''
  componentTypes.value = []
  load()
}

function onComponentTypeChange(e) {
  selectedComponentType.value = componentTypes.value[e.detail.value] || ''
  load()
}

onMounted(load)
</script>

<style scoped>
.container { padding: 20rpx; }
.header { padding: 20rpx 0; }
.title { font-size: 36rpx; font-weight: bold; }
.filters { display: flex; gap: 16rpx; margin-bottom: 20rpx; }
.filter-btn { display: inline-block; padding: 12rpx 24rpx; background: #EDF0F4; border-radius: 4rpx; font-size: 26rpx; color: #171D26; }
.loading { text-align: center; padding: 100rpx 0; color: #626F7D; }
.card { background: #fff; border-radius: 4rpx; padding: 20rpx; margin-bottom: 16rpx; }
.card-row { display: flex; gap: 8rpx; margin-bottom: 10rpx; }
.badge { font-size: 22rpx; padding: 4rpx 12rpx; border-radius: 4rpx; background: #e8f4ff; color: #226CB3; }
.badge-type { background: #fff3e0; color: #E28A13; }
.desc { font-size: 28rpx; color: #171D26; line-height: 1.6; margin-bottom: 8rpx; }
.result-row { display: flex; gap: 16rpx; align-items: center; }
.result { font-size: 26rpx; font-weight: bold; color: #226CB3; }
.clause { font-size: 22rpx; color: #626F7D; }
.empty { text-align: center; padding: 100rpx 0; color: #626F7D; }
</style>
