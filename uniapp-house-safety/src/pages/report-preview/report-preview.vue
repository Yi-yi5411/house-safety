<template>
  <view class="container">
    <!-- 报告标题 -->
    <view class="report-header">
      <text class="report-title">房屋安全鉴定报告</text>
      <text class="report-subtitle">{{ survey.address || '-' }}</text>
      <text v-if="survey.survey_no || survey.surveyNo" class="report-no">鉴定编号：{{ survey.survey_no || survey.surveyNo }}</text>
    </view>

    <!-- 一、房屋基本信息 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">一、房屋基本信息</text>
      </view>
      <view class="info-grid">
        <view class="info-row">
          <text class="info-label">房屋地址</text>
          <text class="info-value">{{ survey.address || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">房屋名称</text>
          <text class="info-value">{{ survey.house_name || survey.houseName || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">建造年代</text>
          <text class="info-value">{{ survey.build_year || survey.buildYear || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">结构类型</text>
          <text class="info-value">{{ survey.structure_type || survey.structureType || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">楼层数</text>
          <text class="info-value">{{ (survey.floor_count || survey.floorCount) ? `${survey.floor_count || survey.floorCount}层` : '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">建筑面积</text>
          <text class="info-value">{{ (survey.build_area || survey.buildArea) ? `${survey.build_area || survey.buildArea}㎡` : '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">檐口高度</text>
          <text class="info-value">{{ (survey.eaves_height || survey.eavesHeight) ? `${survey.eaves_height || survey.eavesHeight}m` : '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">设计用途</text>
          <text class="info-value">{{ survey.design_usage || survey.designUsage || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">现用途</text>
          <text class="info-value">{{ survey.current_usage || survey.currentUsage || '-' }}</text>
        </view>
      </view>
    </view>

    <!-- 二、产权与委托信息 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">二、产权与委托信息</text>
      </view>
      <view class="info-grid">
        <view class="info-row">
          <text class="info-label">产权人</text>
          <text class="info-value">{{ survey.property_owner || survey.propertyOwner || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">使用人</text>
          <text class="info-value">{{ survey.property_user || survey.propertyUser || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">产权性质</text>
          <text class="info-value">{{ survey.property_nature || survey.propertyNature || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">委托人</text>
          <text class="info-value">{{ survey.client_name || survey.clientName || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">联系人</text>
          <text class="info-value">{{ survey.contact_person || survey.contactPerson || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">联系电话</text>
          <text class="info-value">{{ survey.contact_phone || survey.contactPhone || '-' }}</text>
        </view>
      </view>
    </view>

    <!-- 三、自建房专项信息 -->
    <view v-if="hasSelfBuildInfo" class="section">
      <view class="section-header">
        <text class="section-title">三、自建房专项信息</text>
      </view>
      <view class="info-grid">
        <view v-if="(survey.is_self_building !== undefined || survey.isSelfBuilding !== undefined)" class="info-row">
          <text class="info-label">是否自建房</text>
          <text class="info-value">{{ (survey.is_self_building || survey.isSelfBuilding) ? '是' : '否' }}</text>
        </view>
        <view v-if="(survey.is_commercial_self_building !== undefined || survey.isCommercialSelfBuilding !== undefined)" class="info-row">
          <text class="info-label">经营性自建房</text>
          <text class="info-value">{{ (survey.is_commercial_self_building || survey.isCommercialSelfBuilding) ? '是' : '否' }}</text>
        </view>
        <view v-if="(survey.is_rural_dangerous_repair !== undefined || survey.isRuralDangerousRepair !== undefined)" class="info-row">
          <text class="info-label">农危房改造</text>
          <text class="info-value">{{ (survey.is_rural_dangerous_repair || survey.isRuralDangerousRepair) ? '是' : '否' }}</text>
        </view>
        <view v-if="(survey.is_protected_building !== undefined || survey.isProtectedBuilding !== undefined)" class="info-row">
          <text class="info-label">优保建筑</text>
          <text class="info-value">{{ (survey.is_protected_building || survey.isProtectedBuilding) ? '是' : '否' }}</text>
        </view>
        <view v-if="(survey.is_training_institution !== undefined || survey.isTrainingInstitution !== undefined)" class="info-row">
          <text class="info-label">校外培训机构</text>
          <text class="info-value">{{ (survey.is_training_institution || survey.isTrainingInstitution) ? '是' : '否' }}</text>
        </view>
      </view>
    </view>

    <!-- 四、鉴定结论 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">{{ conclusionNum }}、鉴定结论</text>
      </view>
      <view class="conclusion-box" :class="`level-${survey.conclusion}`">
        <text class="conclusion-level">{{ survey.conclusion || '待评定' }}级</text>
        <text class="conclusion-text">{{ survey.basic_evaluation || survey.basicEvaluation || '暂无评定结果' }}</text>
        <text v-if="aiReasoning.riskLevel" class="conclusion-text">安全风险等级：{{ aiReasoning.riskLevel }}</text>
      </view>
    </view>

    <!-- 五、损坏构件统计 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">{{ statsNum }}、损坏构件统计</text>
      </view>
      <view class="damage-stats">
        <view class="stat-item">
          <text class="stat-count">{{ stats.minor }}</text>
          <text class="stat-label">轻微损坏</text>
        </view>
        <view class="stat-item">
          <text class="stat-count">{{ stats.moderate }}</text>
          <text class="stat-label">中等损坏</text>
        </view>
        <view class="stat-item">
          <text class="stat-count">{{ stats.severe }}</text>
          <text class="stat-label">严重损坏</text>
        </view>
        <view class="stat-item">
          <text class="stat-count">{{ stats.dangerous }}</text>
          <text class="stat-label">危险点</text>
        </view>
      </view>
    </view>

    <!-- 六、损坏构件明细 -->
    <view v-if="damageList.length > 0" class="section">
      <view class="section-header">
        <text class="section-title">{{ detailsNum }}、损坏构件明细</text>
      </view>
      <view class="damage-list">
        <view v-for="(item, index) in damageList" :key="item.id" class="damage-item">
          <view class="damage-header">
            <text class="damage-name">{{ index + 1 }}. {{ item.componentType || item.name }}</text>
            <text class="damage-level" :class="`level-${item.damageLevel || item.damage_level}`">
              {{ getDamageLevelText(item.damageLevel || item.damage_level) }}
            </text>
          </view>
          <text class="damage-desc">{{ item.damageDesc || item.damage_description || '-' }}</text>
          <text class="damage-meta">轴线/部位：{{ item.position || item.axisLine || item.axis_line || '/' }}</text>
          <text v-if="item.ai_evaluation_result || item.aiEvaluationResult" class="damage-meta">
            评定结果：{{ item.ai_evaluation_result || item.aiEvaluationResult }}
            <text v-if="item.ai_evaluation_clause || item.aiEvaluationClause" class="clause-ref">（依据：{{ item.ai_evaluation_clause || item.aiEvaluationClause }}）</text>
          </text>
          <!-- 已勾选标准明细 -->
          <view v-if="(item.checkedItemIds || item.checked_item_ids || []).length > 0" class="checked-items">
            <text class="checked-title">已勾选标准：</text>
            <view v-for="sid in (item.checkedItemIds || item.checked_item_ids || [])" :key="sid" class="checked-row">
              <text class="checked-bullet">•</text>
              <text class="checked-desc">{{ getStandardDesc(sid) }}</text>
              <text v-if="getStandardResult(sid)" class="checked-badge" :style="{ background: getResultColor(getStandardResult(sid)) }">{{ getStandardResult(sid) }}</text>
              <text v-if="getStandardClause(sid)" class="checked-clause">{{ getStandardClause(sid) }}</text>
              <!-- 描述值 -->
              <text v-if="getDescValues(sid, item).length > 0" class="checked-values">
                [{{ getDescValues(sid, item).join(', ') }}]
              </text>
            </view>
          </view>
          <view v-if="item.photos && item.photos.length > 0" class="damage-photos">
            <image
              v-for="(photo, pi) in item.photos.slice(0, 3)"
              :key="pi"
              :src="photo"
              class="damage-photo"
              mode="aspectFill"
              @click="previewImage(photo, item.photos)"
            />
            <text v-if="item.photos.length > 3" class="photo-more">+{{ item.photos.length - 3 }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 七、检测结果 -->
    <view v-if="structuralTests.length > 0" class="section">
      <view class="section-header">
        <text class="section-title">{{ testsNum }}、结构检测结果</text>
      </view>
      <view v-for="test in structuralTests" :key="test.id" class="test-item">
        <view class="info-row">
          <text class="info-label">检测单位</text>
          <text class="info-value">{{ test.testUnit || test.test_unit || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">检测人员</text>
          <text class="info-value">{{ test.testPersonnel || test.test_personnel || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">报告编号</text>
          <text class="info-value">{{ test.reportNo || test.report_no || '-' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">安全等级</text>
          <text class="info-value">{{ test.safetyLevel || test.safety_level || '-' }}</text>
        </view>
      </view>
    </view>

    <!-- 处理建议 -->
    <view v-if="aiReasoning.suggestion" class="section">
      <view class="section-header">
        <text class="section-title">{{ suggestionNum }}、处理建议</text>
      </view>
      <view class="suggestion-box">
        <text class="suggestion-text">{{ aiReasoning.suggestion }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="btn-action btn-edit" @click="handleEdit">编辑</button>
      <button class="btn-action btn-export" @click="handleExportDocx">导出Word</button>
      <button class="btn-action btn-pdf" @click="handleExportPdf">导出PDF</button>
      <button class="btn-action btn-original" @click="handleExportOriginal">导出原始记录</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSurveyDetail } from '@/api/survey.js'
import { getComponentCheckList, getEvaluationStandards } from '@/api/damage-component.js'
import { getStructuralTestResults } from '@/api/structural-test.js'
import { exportReportDocx, exportReportPdf, exportOriginalRecordDocx } from '@/api/report.js'

const surveyId = ref('')
const survey = ref({})
const damageList = ref([])
const structuralTests = ref([])
const standardsList = ref([])

const aiReasoning = computed(() => {
  const ai = survey.value.aiReasoningResult || survey.value.ai_reasoning_result || {}
  return typeof ai === 'object' ? ai : {}
})

const hasSelfBuildInfo = computed(() => {
  const s = survey.value
  return (s.is_self_building !== undefined || s.isSelfBuilding !== undefined) ||
    (s.is_commercial_self_building !== undefined || s.isCommercialSelfBuilding !== undefined) ||
    (s.is_rural_dangerous_repair !== undefined || s.isRuralDangerousRepair !== undefined)
})

const sectionOffset = computed(() => hasSelfBuildInfo.value ? 1 : 0)
const conclusionNum = computed(() => 3 + sectionOffset.value)
const statsNum = computed(() => 4 + sectionOffset.value)
const detailsNum = computed(() => 5 + sectionOffset.value)
const testsNum = computed(() => 6 + sectionOffset.value + (damageList.value.length > 0 ? 1 : 0))
const suggestionNum = computed(() => 6 + sectionOffset.value + (damageList.value.length > 0 ? 1 : 0) + (structuralTests.value.length > 0 ? 1 : 0))

const stats = computed(() => {
  const result = { minor: 0, moderate: 0, severe: 0, dangerous: 0 }
  damageList.value.forEach(item => {
    const level = item.damageLevel || item.damage_level
    if (result[level] !== undefined) {
      result[level]++
    }
  })
  return result
})

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  surveyId.value = currentPage.options.id || ''
  loadReportData()
})

const loadReportData = async () => {
  try {
    const [surveyRes, damageRes, testRes, stdRes] = await Promise.all([
      getSurveyDetail(surveyId.value),
      getComponentCheckList(surveyId.value),
      getStructuralTestResults(surveyId.value).catch(() => ({ items: [] })),
      getEvaluationStandards()
    ])
    survey.value = surveyRes
    damageList.value = damageRes.items || damageRes || []
    structuralTests.value = testRes.items || []
    standardsList.value = stdRes.items || stdRes || []
  } catch (error) {
    console.error('加载报告数据失败:', error)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const handleEdit = () => {
  uni.navigateTo({ url: `/pages/data-collection/data-collection?id=${surveyId.value}` })
}

const handleExportDocx = () => {
  handleExport(exportReportDocx(surveyId.value), '报告.docx')
}

const handleExportPdf = () => {
  handleExport(exportReportPdf(surveyId.value), '报告.pdf')
}

const handleExportOriginal = () => {
  handleExport(exportOriginalRecordDocx(surveyId.value), '原始记录.docx')
}

const handleExport = (url, filename) => {
  uni.showLoading({ title: '下载中...' })
  const token = uni.getStorageSync('token')
  uni.downloadFile({
    url,
    header: { 'Authorization': token ? `Bearer ${token}` : '' },
    success: (res) => {
      uni.hideLoading()
      if (res.statusCode === 200) {
        uni.openDocument({
          filePath: res.tempFilePath,
          success: () => uni.showToast({ title: '打开成功', icon: 'success' }),
          fail: () => uni.showToast({ title: '文件已保存', icon: 'success' })
        })
      } else {
        uni.showToast({ title: '下载失败', icon: 'none' })
      }
    },
    fail: () => {
      uni.hideLoading()
      uni.showToast({ title: '下载失败', icon: 'none' })
    }
  })
}

const previewImage = (url, urls) => {
  uni.previewImage({
    current: url,
    urls: urls || [url]
  })
}

const getDamageLevelText = (level) => {
  const map = {
    minor: '轻微',
    moderate: '中等',
    severe: '严重',
    dangerous: '危险'
  }
  return map[level] || level
}

const getResultColor = (r) => ({ '完好': '#2EA65E', '基本完好': '#226CB3', '一般损坏': '#E28A13', '严重损坏': '#D43535', '危险': '#D43535', '危险状态': '#D43535' }[r] || '#626F7D')
const getStandardDesc = (id) => { const s = standardsList.value.find(x => x.id === id); return s ? s.description || '' : '' }
const getStandardResult = (id) => { const s = standardsList.value.find(x => x.id === id); return s ? s.evaluationResult || s.evaluation_result || '' : '' }
const getStandardClause = (id) => { const s = standardsList.value.find(x => x.id === id); return s ? s.evaluationClause || s.evaluation_clause || '' : '' }
const getDescValues = (sid, item) => { const dv = item.descriptionValues || item.description_values || {}; return dv[sid] || [] }
</script>

<style scoped>
.container {
  padding: 20rpx;
  padding-bottom: 160rpx;
}

.report-header {
  text-align: center;
  padding: 40rpx 0;
  background-color: #ffffff;
  border-radius: 4rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.02);
}

.report-title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #171D26;
  margin-bottom: 16rpx;
}

.report-subtitle {
  font-size: 28rpx;
  color: #626F7D;
}

.report-no {
  display: block;
  font-size: 24rpx;
  color: #626F7D;
  margin-top: 8rpx;
}

.section {
  background-color: #ffffff;
  border-radius: 4rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.02);
}

.section-header {
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 2rpx solid #226CB3;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #171D26;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.info-row {
  display: flex;
  align-items: flex-start;
  padding: 12rpx 0;
  border-bottom: 1rpx dashed #DBDFE4;
}

.info-label {
  width: 160rpx;
  font-size: 28rpx;
  color: #626F7D;
  flex-shrink: 0;
}

.info-value {
  flex: 1;
  font-size: 28rpx;
  color: #171D26;
  word-break: break-all;
}

.conclusion-box {
  padding: 24rpx;
  border-radius: 4rpx;
  text-align: center;
}

.level-A { background-color: #E8F0F8; border-left: 8rpx solid #2EA65E; }
.level-B { background-color: #FBF0E0; border-left: 8rpx solid #E28A13; }
.level-C { background-color: #FAEAEA; border-left: 8rpx solid #E28A13; }
.level-D { background-color: #FAEAEA; border-left: 8rpx solid #D43535; }

.conclusion-level {
  display: block;
  font-size: 56rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
}

.level-A .conclusion-level { color: #2EA65E; }
.level-B .conclusion-level { color: #E28A13; }
.level-C .conclusion-level { color: #E28A13; }
.level-D .conclusion-level { color: #D43535; }

.conclusion-text {
  font-size: 28rpx;
  color: #454D59;
  line-height: 1.6;
}

.damage-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.stat-item {
  text-align: center;
  padding: 24rpx;
  background-color: #EDF0F4;
  border-radius: 4rpx;
}

.stat-count {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #226CB3;
  margin-bottom: 8rpx;
}

.stat-label { font-size: 24rpx; color: #626F7D; }

.damage-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.damage-item {
  padding: 20rpx;
  background-color: #EDF0F4;
  border-radius: 4rpx;
}

.damage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.damage-name {
  font-size: 30rpx;
  font-weight: bold;
  color: #171D26;
}

.damage-level {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
  color: #ffffff;
}

.level-minor { background-color: #2EA65E; }
.level-moderate { background-color: #E28A13; }
.level-severe { background-color: #D43535; }
.level-dangerous { background-color: #D43535; }

.damage-desc {
  font-size: 26rpx;
  color: #454D59;
  line-height: 1.5;
  margin-bottom: 8rpx;
}

.damage-meta {
  display: block;
  font-size: 24rpx;
  color: #626F7D;
  margin-top: 4rpx;
}

.damage-photos {
  display: flex;
  gap: 8rpx;
  margin-top: 12rpx;
}

.damage-photo {
  width: 120rpx;
  height: 120rpx;
  border-radius: 4rpx;
}

.photo-more {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120rpx;
  height: 120rpx;
  background-color: #DBDFE4;
  border-radius: 4rpx;
  font-size: 24rpx;
  color: #626F7D;
}

.test-item {
  padding: 16rpx;
  background-color: #EDF0F4;
  border-radius: 4rpx;
  margin-bottom: 16rpx;
}

.suggestion-box {
  padding: 20rpx;
  background-color: #E8F0F8;
  border-radius: 4rpx;
  border-left: 8rpx solid #226CB3;
}

.suggestion-text {
  font-size: 28rpx;
  color: #454D59;
  line-height: 1.6;
}

.action-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  padding: 16rpx;
  background-color: #ffffff;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.btn-action {
  flex: 1;
  min-width: 140rpx;
  border: none;
  border-radius: 4rpx;
  padding: 20rpx 0;
  font-size: 26rpx;
  color: #ffffff;
}

.btn-edit { background-color: #626F7D; }
.btn-export { background-color: #226CB3; }
.btn-pdf { background-color: #E28A13; }
.btn-original { background-color: #2EA65E; }
</style>
