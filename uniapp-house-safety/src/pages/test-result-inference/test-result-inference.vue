<template>
  <view class="container">
    <view class="header">
      <text class="title">检测结果推理</text>
    </view>

    <!-- AI 智能推理按钮 -->
    <view class="ai-reason-section">
      <button class="btn-ai-reason" :loading="aiReasonLoading" @click="handleAIReason">
        AI智能推理全部检测结果
      </button>
      <text class="ai-hint">基于房屋概况和构件检查数据，一键生成结构检测、损坏综述、鉴定结论等全部内容</text>
    </view>

    <!-- 标签切换 -->
    <view class="tabs">
      <view
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <text>{{ tab.label }}</text>
      </view>
    </view>

    <!-- Tab 1: 结构检测 -->
    <view v-show="activeTab === 'structural'" class="tab-content">
      <view v-if="loading.structural" class="loading">加载中...</view>
      <view v-else>
        <view v-if="testResult" class="card">
          <view class="form-row">
            <text class="label">检测单位</text>
            <input v-model="testResult.test_unit" placeholder="检测单位" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <text class="label">资质证书编号</text>
            <input v-model="testResult.certificate_no" placeholder="证书编号" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <text class="label">检测人员</text>
            <input v-model="testResult.test_personnel" placeholder="检测人员" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <text class="label">报告编号</text>
            <input v-model="testResult.report_no" placeholder="报告编号" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <text class="label">检测日期</text>
            <picker mode="date" :value="testResult.test_date" @change="(e) => { testResult.test_date = e.detail.value; saveStructural() }">
              <text>{{ testResult.test_date || '选择日期' }}</text>
            </picker>
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">主要检测内容</text>
              <button class="btn-ai-mini" :loading="aiFields.main_test" @click="genField('main_test_content')">AI生成</button>
            </view>
            <textarea v-model="testResult.main_test_content" placeholder="主要检测内容" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">检测依据标准</text>
              <button class="btn-ai-mini" :loading="aiFields.test_standards" @click="genField('test_standards')">AI生成</button>
            </view>
            <textarea v-model="testResult.test_standards" placeholder="检测依据标准" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">主要检测成果</text>
              <button class="btn-ai-mini" :loading="aiFields.test_results" @click="genField('test_results_summary')">AI生成</button>
            </view>
            <textarea v-model="testResult.test_results_summary" placeholder="检测成果摘要" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">损坏情况综述</text>
              <button class="btn-ai-mini" :loading="aiFields.damage_summary" @click="genField('damage_summary')">AI生成</button>
            </view>
            <textarea v-model="testResult.damage_summary" placeholder="损坏情况综述" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">原因分析</text>
              <button class="btn-ai-mini" :loading="aiFields.cause_analysis" @click="genField('cause_analysis')">AI生成</button>
            </view>
            <textarea v-model="testResult.cause_analysis" placeholder="原因分析" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">鉴定结论</text>
              <button class="btn-ai-mini" :loading="aiFields.conclusion" @click="genField('conclusion')">AI生成</button>
            </view>
            <textarea v-model="testResult.conclusion" placeholder="鉴定结论" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">处理意见</text>
              <button class="btn-ai-mini" :loading="aiFields.handling_suggestion" @click="genField('handling_suggestion')">AI生成</button>
            </view>
            <textarea v-model="testResult.handling_suggestion" placeholder="处理建议" @blur="saveStructural" />
          </view>
          <view class="form-row">
            <view class="label-row">
              <text class="label">安全等级</text>
              <button class="btn-ai-mini" :loading="aiFields.safety_level" @click="genField('safety_level')">AI生成</button>
            </view>
            <view class="safety-options">
              <text
                v-for="level in ['A', 'B', 'C', 'D']"
                :key="level"
                class="safety-item"
                :class="{ 'safety-active': testResult.safety_level === level }"
                @click="testResult.safety_level = level; saveStructural()"
              >{{ level }}</text>
            </view>
          </view>
        </view>
        <view v-else class="empty-hint">
          <text>暂无检测结果，点击上方"AI智能推理"按钮生成</text>
        </view>
      </view>
    </view>

    <!-- Tab 2: 检测图片 -->
    <view v-show="activeTab === 'images'" class="tab-content">
      <view v-if="loading.images" class="loading">加载中...</view>
      <view v-else>
        <view v-for="group in imageGroups" :key="group.type" class="image-group">
          <text class="group-title">{{ group.label }}</text>
          <view class="image-grid">
            <view v-for="img in group.images" :key="img.id" class="image-item">
              <image :src="img.image_url" mode="aspectFill" class="img" @click="previewImage(img.image_url)" />
              <view class="img-info">
                <text class="img-label">{{ img.label || group.label }}</text>
                <button class="btn-img-delete" @click="deleteImage(img.id)">×</button>
              </view>
            </view>
            <view class="image-item add-item" @click="addImage(group.type)">
              <text class="add-icon">+</text>
              <text class="add-text">添加</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Tab 3: 签字盖章 -->
    <view v-show="activeTab === 'signatures'" class="tab-content">
      <view v-if="loading.signatures" class="loading">加载中...</view>
      <view v-else>
        <view v-for="sig in signatures" :key="sig.id" class="sig-card">
          <view class="sig-header">
            <text class="sig-type">{{ typeLabel(sig.type) }}</text>
            <button class="btn-delete" @click="deleteSignature(sig.id)">删除</button>
          </view>
          <view class="form-row">
            <text class="label">签署人姓名</text>
            <input v-model="sig.signatory_name" placeholder="请输入姓名" @blur="updateSignature(sig)" />
          </view>
          <view class="form-row">
            <text class="label">签署日期</text>
            <picker mode="date" :value="sig.sign_date" @change="(e) => { sig.sign_date = e.detail.value; updateSignature(sig) }">
              <text>{{ sig.sign_date || '请选择日期' }}</text>
            </picker>
          </view>
          <view class="form-row">
            <text class="label">签名图片</text>
            <button class="btn-upload" @click="uploadSigImage(sig)">上传图片</button>
            <image v-if="sig.image_url" :src="sig.image_url" mode="widthFix" class="sig-img" />
          </view>
        </view>
        <button class="btn-add" @click="addSignature">+ 新增签字盖章</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getStructuralTestResults, createStructuralTestResult, updateStructuralTestResult } from '@/api/structural-test.js'
import { getTestImages, createTestImage, deleteTestImage as apiDeleteTestImage } from '@/api/test-image.js'
import { getSignatures, createSignature, updateSignature as apiUpdateSignature, deleteSignature as apiDeleteSignature } from '@/api/signature.js'
import { getSurveyDetail } from '@/api/survey.js'
import {
  generateMainTestContent, generateTestStandards, generateTestResults,
  generateDamageSummary, generateCauseAnalysis, generateConclusion,
  generateHandlingSuggestion, generateSafetyLevel
} from '@/api/ai.js'
import request from '@/api/request.js'

const surveyId = ref('')
const activeTab = ref('structural')
const aiReasonLoading = ref(false)

const tabs = [
  { key: 'structural', label: '结构检测' },
  { key: 'images', label: '检测图片' },
  { key: 'signatures', label: '签字盖章' }
]

// === 结构检测 ===
const testResult = ref(null)
const loading = reactive({ structural: true, images: true, signatures: true })
const aiFields = reactive({
  main_test: false, test_standards: false, test_results: false,
  damage_summary: false, cause_analysis: false, conclusion: false,
  handling_suggestion: false, safety_level: false
})

// === 检测图片 ===
const survey = ref({})
const images = ref([])
const IMAGE_TYPES = [
  { type: 'elevation_front', label: '正立面图' },
  { type: 'elevation_back', label: '背立面图' },
  { type: 'floor_plan', label: '平面图' },
  { type: 'site_plan', label: '总平面图' }
]
const imageGroups = computed(() => IMAGE_TYPES.map(t => ({
  ...t,
  images: images.value.filter(img => img.type === t.type)
})))

// === 签字盖章 ===
const signatures = ref([])
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

// === AI 智能推理全部 ===
async function handleAIReason() {
  aiReasonLoading.value = true
  try {
    // 获取最新数据
    const [surveyDetail, componentRes] = await Promise.all([
      getSurveyDetail(surveyId.value).catch(() => ({})),
      request.get(`/components?survey_id=${surveyId.value}`).catch(() => ({ items: [] }))
    ])
    const components = componentRes?.items || componentRes || []

    const buildingProfile = {
      address: surveyDetail.address || survey.value.address || '',
      buildYear: surveyDetail.build_year || survey.value.build_year || '',
      floorCount: surveyDetail.floor_count || survey.value.floor_count || '',
      buildArea: surveyDetail.build_area || survey.value.build_area || '',
      structureType: surveyDetail.structure_type || survey.value.structure_type || '',
      houseName: surveyDetail.house_name || survey.value.house_name || '',
      propertyOwner: surveyDetail.property_owner || survey.value.property_owner || '',
    }

    const res = await request.post('/ai/structural-reason', {
      building_profile: buildingProfile,
      component_checks: components
    })

    if (res) {
      // Ensure test result exists
      if (!testResult.value) {
        testResult.value = await createStructuralTestResult({
          survey_id: surveyId.value,
          test_unit: '',
          certificate_no: '', test_personnel: '', report_no: '',
          main_test_content: '', test_standards: '', test_results_summary: '',
          damage_summary: '', cause_analysis: '',
          conclusion: '', handling_suggestion: ''
        })
      }

      // Fill all AI-generated fields
      if (res.main_test_content) testResult.value.main_test_content = res.main_test_content
      if (res.test_standards) testResult.value.test_standards = res.test_standards
      if (res.test_results_summary) testResult.value.test_results_summary = res.test_results_summary
      if (res.damage_summary) testResult.value.damage_summary = res.damage_summary
      if (res.cause_analysis) testResult.value.cause_analysis = res.cause_analysis
      if (res.conclusion) testResult.value.conclusion = res.conclusion
      if (res.handling_suggestion) testResult.value.handling_suggestion = res.handling_suggestion
      if (res.safety_level) {
        const m = String(res.safety_level).match(/[ABCD](?=\s|级|$)/i)
        testResult.value.safety_level = m ? m[0].toUpperCase() : String(res.safety_level).trim().charAt(0).toUpperCase()
      }
      await saveStructural()
      uni.showToast({ title: 'AI推理完成', icon: 'success' })
    }
  } catch (e) {
    console.error(e)
    uni.showToast({ title: 'AI推理失败', icon: 'none' })
  } finally { aiReasonLoading.value = false }
}

// === 单项AI生成 ===
async function genField(field) {
  const loadingKey = {
    main_test_content: 'main_test', test_standards: 'test_standards', test_results_summary: 'test_results',
    damage_summary: 'damage_summary', cause_analysis: 'cause_analysis', conclusion: 'conclusion',
    handling_suggestion: 'handling_suggestion', safety_level: 'safety_level'
  }
  const lk = loadingKey[field]
  if (!lk) return
  aiFields[lk] = true
  try {
    if (!testResult.value) {
      testResult.value = await createStructuralTestResult({
        survey_id: surveyId.value,
        test_unit: '', certificate_no: '', test_personnel: '', report_no: '',
        main_test_content: '', test_standards: '', test_results_summary: '',
        damage_summary: '', cause_analysis: '', conclusion: '', handling_suggestion: ''
      })
    }

    // Fetch fresh survey data and component checks for context
    const [surveyDetail, compRes] = await Promise.all([
      getSurveyDetail(surveyId.value).catch(() => ({})),
      request.get(`/components?survey_id=${surveyId.value}`).catch(() => ({ items: [] }))
    ])
    const components = compRes?.items || compRes || []

    // Build building profile as proper object (not JSON string)
    const bp = {
      address: surveyDetail.address || survey.value.address || '',
      buildYear: surveyDetail.build_year || survey.value.build_year || '',
      floorCount: surveyDetail.floor_count || survey.value.floor_count || '',
      buildArea: surveyDetail.build_area || survey.value.build_area || '',
      structureType: surveyDetail.structure_type || survey.value.structure_type || '',
      houseName: surveyDetail.house_name || survey.value.house_name || '',
      propertyOwner: surveyDetail.property_owner || survey.value.property_owner || '',
    }

    let res
    switch (field) {
      case 'main_test_content':
        res = await generateMainTestContent(bp)
        break
      case 'test_standards':
        res = await generateTestStandards(testResult.value.main_test_content || '')
        break
      case 'test_results_summary':
        res = await generateTestResults(bp, testResult.value.main_test_content || '', testResult.value.test_standards || '', components)
        break
      case 'damage_summary':
        res = await generateDamageSummary(bp, components)
        break
      case 'cause_analysis':
        res = await generateCauseAnalysis(bp, components)
        break
      case 'conclusion':
        res = await generateConclusion(bp, components)
        break
      case 'handling_suggestion':
        res = await generateHandlingSuggestion(bp, components)
        break
      case 'safety_level':
        res = await generateSafetyLevel(bp, components)
        break
    }
    if (res?.content) {
      if (field === 'safety_level') {
        // Extract A/B/C/D from the response
        const m = res.content.match(/[ABCD](?=\s|级|$)/i)
        testResult.value.safety_level = m ? m[0].toUpperCase() : res.content.trim().charAt(0).toUpperCase()
      } else {
        testResult.value[field] = res.content
      }
      await saveStructural()
      uni.showToast({ title: '生成成功', icon: 'success' })
    }
  } catch (e) { console.error(e); uni.showToast({ title: '生成失败', icon: 'none' }) }
  finally { aiFields[lk] = false }
}

// === 结构检测 CRUD ===
async function loadStructural() {
  try {
    const result = await getStructuralTestResults(surveyId.value)
    const items = result?.items || result || []
    testResult.value = Array.isArray(items) ? items[0] || null : items
  } catch (e) { /* handled */ }
  finally { loading.structural = false }
}

async function saveStructural() {
  if (!testResult.value) return
  try {
    if (testResult.value.id) {
      await updateStructuralTestResult(surveyId.value, testResult.value.id, testResult.value)
    } else {
      const created = await createStructuralTestResult({ survey_id: surveyId.value, ...testResult.value })
      if (created) testResult.value = created
    }
  } catch (e) { /* handled */ }
}

// === 检测图片 CRUD ===
async function loadImages() {
  try {
    const [imgRes, surveyRes] = await Promise.all([
      getTestImages(surveyId.value).catch(() => []),
      getSurveyDetail(surveyId.value).catch(() => ({}))
    ])
    images.value = imgRes?.items || imgRes || []
    survey.value = surveyRes || {}
  } catch (e) { /* handled */ }
  finally { loading.images = false }
}

function genImageLabel(type) {
  const count = images.value.filter(i => i.type === type).length + 1
  const labels = {
    elevation_front: `正立面示意图 ${count}`,
    elevation_back: `背立面示意图 ${count}`,
    floor_plan: survey.value.floorCount ? `一层平面及局部损坏示意图` : `平面图 ${count}`,
    site_plan: '总平面示意图'
  }
  return labels[type] || `${type} ${count}`
}

async function addImage(type) {
  const label = genImageLabel(type)
  uni.showModal({
    title: '添加图片', content: `标签：${label}`, confirmText: '上传',
    success: async (modalRes) => {
      if (!modalRes.confirm) return
      uni.chooseImage({
        count: 1,
        success: async (res) => {
          try {
            const url = await request.upload(res.tempFilePaths[0], '/upload/image')
            const img = await createTestImage(surveyId.value, { type, image_url: url, label, sort_order: images.value.length })
            images.value.push(img)
          } catch (e) { /* handled */ }
        }
      })
    }
  })
}

async function deleteImage(id) {
  try {
    await apiDeleteTestImage(surveyId.value, id)
    images.value = images.value.filter(i => i.id !== id)
  } catch (e) { /* handled */ }
}

function previewImage(url) { uni.previewImage({ urls: [url] }) }

// === 签字盖章 CRUD ===
async function loadSignatures() {
  try {
    const result = await getSignatures(surveyId.value)
    signatures.value = result?.items || result || []
  } catch (e) {
    signatures.value = []
  }
  finally { loading.signatures = false }
}

async function addSignature() {
  const type = SIGNATURE_TYPES[signatures.value.length % SIGNATURE_TYPES.length].value
  try {
    const sig = await createSignature(surveyId.value, { type })
    signatures.value.push(sig)
  } catch (e) { /* handled */ }
}

async function updateSignature(sig) {
  try {
    await apiUpdateSignature(surveyId.value, sig.id, {
      signatory_name: sig.signatory_name, image_url: sig.image_url, sign_date: sig.sign_date
    })
  } catch (e) { /* handled */ }
}

async function deleteSignature(id) {
  try {
    await apiDeleteSignature(surveyId.value, id)
    signatures.value = signatures.value.filter(s => s.id !== id)
  } catch (e) { /* handled */ }
}

async function uploadSigImage(sig) {
  uni.chooseImage({
    count: 1,
    success: async (res) => {
      try {
        const url = await request.upload(res.tempFilePaths[0], '/upload/image')
        sig.image_url = url
        await updateSignature(sig)
      } catch (e) { /* handled */ }
    }
  })
}

onMounted(async () => {
  const pages = getCurrentPages()
  surveyId.value = pages[pages.length - 1]?.options?.id || ''
  if (!surveyId.value) {
    uni.showToast({ title: '缺少鉴定记录ID', icon: 'none' })
    return
  }
  await loadStructural()
  await loadImages()
  await loadSignatures()
})
</script>

<style scoped>
.container { padding: 20rpx; padding-bottom: 60rpx; }
.header { padding: 20rpx 0; }
.title { font-size: 36rpx; font-weight: bold; color: #171D26; }

/* AI推理按钮 */
.ai-reason-section { text-align: center; margin: 20rpx 0; }
.btn-ai-reason {
  background: linear-gradient(135deg, #226CB3 0%, #1B5A96 100%);
  color: #fff; border: none; border-radius: 8rpx;
  padding: 28rpx 40rpx; font-size: 34rpx; font-weight: bold;
  box-shadow: 0 4rpx 16rpx rgba(34,108,179,0.3);
}
.ai-hint { display: block; font-size: 22rpx; color: #7A7E83; margin-top: 12rpx; }

/* 标签 */
.tabs { display: flex; gap: 0; margin: 24rpx 0; background: #EDF0F4; border-radius: 6rpx; overflow: hidden; }
.tab-item { flex: 1; text-align: center; padding: 20rpx 0; font-size: 28rpx; color: #626F7D; }
.tab-item.active { background: #226CB3; color: #fff; font-weight: bold; }
.tab-content { padding: 10rpx 0; }

.loading { text-align: center; padding: 100rpx 0; color: #626F7D; }
.empty-hint { text-align: center; padding: 80rpx 0; color: #7A7E83; font-size: 26rpx; }

/* 表单 */
.card { background: #fff; border-radius: 6rpx; padding: 24rpx; }
.form-row { margin-bottom: 16rpx; }
.label { font-size: 26rpx; color: #454D59; display: block; margin-bottom: 6rpx; }
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6rpx; }
.form-row input, .form-row textarea {
  border: 1rpx solid #E5E8EC; border-radius: 4rpx; padding: 12rpx;
  font-size: 28rpx; width: 100%; box-sizing: border-box; background: #F9FAFB;
}
.form-row textarea { min-height: 100rpx; }

.btn-ai-mini {
  background: #E28A13; color: #fff; border: none; border-radius: 4rpx;
  padding: 8rpx 20rpx; font-size: 22rpx; line-height: 1.4;
}

/* 安全等级 */
.safety-options { display: flex; gap: 20rpx; margin-top: 8rpx; }
.safety-item {
  width: 80rpx; height: 80rpx; border-radius: 8rpx; background: #EDF0F4;
  display: flex; align-items: center; justify-content: center;
  font-size: 36rpx; font-weight: bold; color: #626F7D;
}
.safety-active { background: #226CB3; color: #fff; }

/* 图片 */
.image-group { margin-bottom: 30rpx; }
.group-title { font-size: 28rpx; font-weight: bold; display: block; margin-bottom: 16rpx; color: #171D26; }
.image-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.image-item { width: 210rpx; background: #fff; border-radius: 4rpx; overflow: hidden; }
.img { width: 210rpx; height: 210rpx; }
.img-info { padding: 8rpx; display: flex; justify-content: space-between; align-items: center; }
.img-label { font-size: 22rpx; color: #454D59; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.btn-img-delete { font-size: 28rpx; color: #D43535; background: none; border: none; padding: 0; line-height: 1; }
.add-item { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 210rpx; border: 2rpx dashed #DBDFE4; background: #F9FAFB; }
.add-icon { font-size: 48rpx; color: #DBDFE4; }
.add-text { font-size: 24rpx; color: #626F7D; margin-top: 8rpx; }

/* 签字 */
.sig-card { background: #fff; border-radius: 6rpx; padding: 24rpx; margin-bottom: 20rpx; }
.sig-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.sig-type { font-size: 30rpx; font-weight: bold; color: #226CB3; }
.btn-delete { font-size: 24rpx; color: #D43535; background: none; border: none; padding: 0; }
.btn-upload { font-size: 24rpx; margin: 8rpx 0; background: #EDF0F4; color: #454D59; border: none; border-radius: 4rpx; padding: 10rpx 24rpx; }
.sig-img { width: 200rpx; margin-top: 8rpx; border-radius: 4rpx; }
.btn-add { background: #226CB3; color: #fff; border: none; border-radius: 4rpx; padding: 24rpx 0; font-size: 28rpx; margin-top: 20rpx; }
</style>
