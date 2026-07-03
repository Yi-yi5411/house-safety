<template>
  <view class="container">
    <view class="header"><text class="title">结构检测结果</text></view>

    <view v-if="loading" class="loading">加载中...</view>

    <view v-else v-for="item in items" :key="item.id" class="card">
      <view class="card-header">
        <text class="subtitle">检测记录</text>
        <button class="btn-delete" @click="handleDelete(item.id)">删除</button>
      </view>

      <view class="form-row">
        <text class="label">检测单位</text>
        <input v-model="item.test_unit" placeholder="检测单位" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">证书编号</text>
        <input v-model="item.certificate_no" placeholder="证书编号" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">检测人员</text>
        <input v-model="item.test_personnel" placeholder="检测人员" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">报告编号</text>
        <input v-model="item.report_no" placeholder="报告编号" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">检测日期</text>
        <picker mode="date" @change="(e) => { item.test_date = e.detail.value; handleUpdate(item) }">
          <text>{{ item.test_date || '选择日期' }}</text>
        </picker>
      </view>
      <view class="form-row">
        <view class="label-row"><text class="label">主要检测内容</text><button class="btn-ai" size="mini" :loading="aiLoading.mainTest" @click="genAI('main_test_content', item)">AI生成</button></view>
        <textarea v-model="item.main_test_content" placeholder="主要检测内容" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <view class="label-row"><text class="label">检测依据标准</text><button class="btn-ai" size="mini" :loading="aiLoading.testStandards" @click="genAI('test_standards', item)">AI生成</button></view>
        <textarea v-model="item.test_standards" placeholder="检测依据标准" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <view class="label-row"><text class="label">检测成果摘要</text><button class="btn-ai" size="mini" :loading="aiLoading.testResults" @click="genAI('test_results_summary', item)">AI生成</button></view>
        <textarea v-model="item.test_results_summary" placeholder="检测成果摘要" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">损坏情况综述</text>
        <textarea v-model="item.damage_summary" placeholder="损坏情况综述" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">原因分析</text>
        <textarea v-model="item.cause_analysis" placeholder="原因分析" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">鉴定结论</text>
        <input v-model="item.conclusion" placeholder="鉴定结论" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">处理建议</text>
        <textarea v-model="item.handling_suggestion" placeholder="处理建议" @blur="() => handleUpdate(item)" />
      </view>
      <view class="form-row">
        <text class="label">安全等级</text>
        <picker mode="selector" :range="['A', 'B', 'C', 'D']" @change="(e) => { item.safety_level = ['A','B','C','D'][e.detail.value]; handleUpdate(item) }">
          <text>{{ item.safety_level || '选择等级' }}</text>
        </picker>
      </view>
    </view>

    <button class="btn-add" @click="handleAdd">+ 新增检测结果</button>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  getStructuralTestResults,
  createStructuralTestResult,
  updateStructuralTestResult,
  deleteStructuralTestResult
} from '@/api/structural-test.js'
import { generateDamageSummary, generateCauseAnalysis, generateConclusion } from '@/api/ai.js'

const surveyId = ref('')
const items = ref([])
const loading = ref(true)
const aiLoading = reactive({ mainTest: false, testStandards: false, testResults: false })

const genAI = async (field, item) => {
  const k = { main_test_content: 'mainTest', test_standards: 'testStandards', test_results_summary: 'testResults' }
  aiLoading[k[field]] = true
  try {
    let res
    if (field === 'main_test_content') res = await generateConclusion(JSON.stringify({ surveyId: surveyId.value }), '')
    else if (field === 'test_standards') res = await generateCauseAnalysis('', '', '')
    else res = await generateDamageSummary('', '')
    if (res && res.content) { item[field] = res.content; await handleUpdate(item); uni.showToast({ title: '生成成功', icon: 'success' }) }
  } catch (e) { console.error(e); uni.showToast({ title: '生成失败', icon: 'none' }) }
  finally { aiLoading[k[field]] = false }
}

async function load() {
  try {
    const result = await getStructuralTestResults(surveyId.value)
    items.value = result.items || result || []
  } catch (e) { /* handled */ }
  finally { loading.value = false }
}

async function handleAdd() {
  try {
    const item = await createStructuralTestResult({
      survey_id: surveyId.value,
      test_unit: '',
      certificate_no: '',
      test_personnel: '',
      report_no: '',
      test_date: '',
      main_test_content: '',
      test_standards: '',
      test_results_summary: '',
      damage_summary: '',
      cause_analysis: '',
      conclusion: '',
      handling_suggestion: '',
      safety_level: ''
    })
    items.value.push(item)
  } catch (e) { /* handled */ }
}

async function handleUpdate(item) {
  try {
    await updateStructuralTestResult(surveyId.value, item.id, item)
  } catch (e) { /* handled */ }
}

async function handleDelete(id) {
  try {
    await deleteStructuralTestResult(surveyId.value, id)
    items.value = items.value.filter(i => i.id !== id)
  } catch (e) { /* handled */ }
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
.card { background: #fff; border-radius: 6rpx; padding: 24rpx; margin-bottom: 20rpx; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.subtitle { font-size: 30rpx; font-weight: bold; }
.btn-delete { font-size: 24rpx; color: #D43535; background: none; border: none; padding: 0; }
.form-row { margin-bottom: 14rpx; }
.label { font-size: 26rpx; color: #454D59; display: block; margin-bottom: 6rpx; }
.form-row input, .form-row textarea {
  border: 1rpx solid #E5E8EC; border-radius: 4rpx; padding: 12rpx; font-size: 28rpx; width: 100%; box-sizing: border-box;
}
.form-row textarea { min-height: 100rpx; }
.btn-add { background: #226CB3; color: #fff; border-radius: 4rpx; margin-top: 20rpx; }
</style>
