<template>
  <view class="container">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <input v-model="keyword" placeholder="搜索鉴定项目..." class="search-input" @confirm="handleSearch" />
      <button class="btn-search" @click="handleSearch">搜索</button>
    </view>

    <!-- 列表 -->
    <view class="list" v-if="list.length > 0">
      <view v-for="item in list" :key="item.id" class="survey-card" @click="handleClick(item)">
        <view class="card-top">
          <view class="card-main">
            <text class="card-address">{{ item.address || item.location || '未命名鉴定' }}</text>
            <text class="card-no" v-if="item.surveyNo || item.survey_no">编号：{{ item.surveyNo || item.survey_no }}</text>
          </view>
          <view class="card-badges">
            <text class="badge-status" :class="'status-' + (item.status || 'draft')">{{ statusText(item.status) }}</text>
            <text v-if="item.riskLevel || item.risk_level" class="badge-risk" :class="'risk-' + (item.riskLevel || item.risk_level)">{{ item.riskLevel || item.risk_level }}</text>
          </view>
        </view>
        <view class="card-meta">
          <text class="meta-item" v-if="item.buildYear">建造：{{ item.buildYear }}年</text>
          <text class="meta-item" v-if="item.structureType">结构：{{ item.structureType }}</text>
          <text class="meta-item" v-if="item.floorCount">{{ item.floorCount }}层</text>
          <text class="meta-item" v-if="item.buildArea">{{ item.buildArea }}㎡</text>
        </view>
        <view class="card-footer">
          <text class="footer-time">{{ formatTime(item.createdAt || item.created_at || item.surveyTime) }}</text>
          <button class="btn-delete" size="mini" @click.stop="handleDelete(item)">删除</button>
        </view>
      </view>
    </view>

    <view v-else-if="!loading" class="empty">
      <text class="empty-text">暂无鉴定记录</text>
      <button class="btn-new" @click="handleAdd">+ 新建鉴定</button>
    </view>

    <view v-if="loading" class="loading"><text>加载中...</text></view>

    <!-- 浮动新建按钮 -->
    <view class="fab" @click="handleAdd"><text class="fab-icon">+</text></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { getSurveyList, createSurvey, deleteSurvey } from '@/api/survey.js'

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const page = ref(1)

onShow(() => loadList())

const loadList = async () => {
  loading.value = true
  try {
    const res = await getSurveyList({ page: page.value, pageSize: 20, keyword: keyword.value })
    list.value = res.items || res || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}

const handleSearch = () => { page.value = 1; loadList() }
const handleAdd = async () => {
  try {
    const res = await createSurvey({ address: '新建鉴定项目' })
    if (res.id) uni.navigateTo({ url: `/pages/data-collection/data-collection?id=${res.id}` })
  } catch (e) { uni.showToast({ title: '创建失败', icon: 'none' }) }
}
const handleClick = (item) => uni.navigateTo({ url: `/pages/data-collection/data-collection?id=${item.id}` })
const handleDelete = (item) => {
  uni.showModal({ title: '确认删除', content: `确定删除"${item.address || '该项目'}"？`, success: async (res) => {
    if (res.confirm) { try { await deleteSurvey(item.id); loadList() } catch (e) { uni.showToast({ title: '删除失败', icon: 'none' }) } }
  }})
}
const statusText = (s) => ({ draft: '草稿', completed: '已完成', exported: '已导出' }[s] || s || '草稿')
const formatTime = (t) => t ? new Date(t).toLocaleDateString('zh-CN') : ''

onPullDownRefresh(() => { loadList().finally(() => uni.stopPullDownRefresh()) })
</script>

<style scoped>
.container { padding: 16rpx; padding-bottom: 140rpx; }
.search-bar { display: flex; gap: 12rpx; padding: 16rpx 0; }
.search-input { flex: 1; height: 64rpx; padding: 0 16rpx; background: #EDF0F4; border-radius: 4rpx; font-size: 28rpx; }
.btn-search { background: #226CB3; color: #fff; border: none; border-radius: 4rpx; padding: 0 30rpx; font-size: 26rpx; }

.list { display: flex; flex-direction: column; gap: 16rpx; }
.survey-card { background: #fff; border-radius: 4rpx; padding: 20rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,.01); }
.card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10rpx; }
.card-main { flex: 1; }
.card-address { font-size: 30rpx; font-weight: bold; color: #171D26; display: block; }
.card-no { font-size: 22rpx; color: #626F7D; margin-top: 4rpx; }
.card-badges { display: flex; gap: 8rpx; flex-shrink: 0; }
.badge-status { font-size: 20rpx; padding: 4rpx 12rpx; border-radius: 6rpx; }
.status-draft { background: #EDF0F4; color: #626F7D; }
.status-completed { background: #E3EDF6; color: #226CB3; }
.status-exported { background: #EBF5EE; color: #2EA65E; }
.badge-risk { font-size: 20rpx; padding: 4rpx 12rpx; border-radius: 6rpx; color: #fff; }
.risk-A { background: #2EA65E; } .risk-B { background: #226CB3; } .risk-C { background: #E28A13; } .risk-D { background: #D43535; }
.card-meta { display: flex; gap: 20rpx; flex-wrap: wrap; margin-top: 8rpx; }
.meta-item { font-size: 24rpx; color: #454D59; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 12rpx; padding-top: 10rpx; border-top: 1rpx solid #EDF0F4; }
.footer-time { font-size: 22rpx; color: #B0B8C2; }
.btn-delete { background: #FAEAEA; color: #D43535; border: none; border-radius: 6rpx; padding: 6rpx 16rpx; font-size: 22rpx; }

.empty { text-align: center; padding: 100rpx 0; }
.empty-text { display: block; font-size: 32rpx; color: #626F7D; margin-bottom: 30rpx; }
.btn-new { background: #226CB3; color: #fff; border: none; border-radius: 4rpx; padding: 20rpx 60rpx; font-size: 28rpx; }
.loading { text-align: center; padding: 40rpx; color: #626F7D; }
.fab { position: fixed; right: 30rpx; bottom: 120rpx; width: 90rpx; height: 90rpx; background: #226CB3; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2rpx 12rpx rgba(34,108,179,.15); }
.fab-icon { font-size: 44rpx; color: #fff; font-weight: bold; }
</style>
