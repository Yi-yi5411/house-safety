<template>
  <view class="container">
    <!-- 步骤导航 -->
    <view class="step-nav">
      <view class="step active"><text class="step-num">1</text><text class="step-text">房屋概况</text></view>
      <view class="step-divider"></view>
      <view class="step step-link" @click="goToDamageRecord"><text class="step-num">2</text><text class="step-text">构件检查</text><text class="step-arrow">→</text></view>
    </view>

    <!-- 构件检查入口按钮 -->
    <button class="btn-inspect-entry" @click="goToDamageRecord">进入构件检查 →</button>

    <!-- 鉴定信息 -->
    <view class="card">
      <view class="card-header"><text class="card-title">鉴定信息</text></view>
      <view class="form-list">
        <view class="form-item"><text class="form-label">鉴定编号</text><input v-model="form.surveyNo" placeholder="鉴定编号" class="form-input" /></view>
        <view class="form-item">
          <text class="form-label">鉴定类别</text>
          <picker mode="selector" :range="surveyTypeOptions" @change="(e) => form.surveyType = surveyTypeOptions[e.detail.value]"><view class="picker-value">{{ form.surveyType || '请选择' }}</view></picker>
        </view>
        <view class="form-item"><text class="form-label">鉴定目的</text><input v-model="form.surveyPurpose" placeholder="鉴定目的" class="form-input" /></view>
        <view class="form-item"><text class="form-label">鉴定面积(㎡)</text><input v-model="form.surveyArea" type="digit" placeholder="建筑面积" class="form-input" /></view>
      </view>
    </view>

    <!-- 委托信息 -->
    <view class="card">
      <view class="card-header"><text class="card-title">委托信息</text></view>
      <view class="form-list">
        <view class="form-item"><text class="form-label">委托单位</text><input v-model="form.clientUnit" placeholder="委托单位" class="form-input" /></view>
        <view class="form-item"><text class="form-label">委托方</text><input v-model="form.clientName" placeholder="委托方" class="form-input" /></view>
        <view class="form-item"><text class="form-label">联系人</text><input v-model="form.contactPerson" placeholder="联系人" class="form-input" /></view>
        <view class="form-item"><text class="form-label">联系电话</text><input v-model="form.contactPhone" type="number" placeholder="联系电话" class="form-input" /></view>
        <view class="form-item"><text class="form-label">委托日期</text><picker mode="date" :value="form.surveyDate" @change="(e) => form.surveyDate = e.detail.value"><view class="picker-value">{{ form.surveyDate || '请选择' }}</view></picker></view>
        <view class="form-item"><text class="form-label">查勘完成日期</text><picker mode="date" :value="form.inspectionDate" @change="(e) => form.inspectionDate = e.detail.value"><view class="picker-value">{{ form.inspectionDate || '请选择' }}</view></picker></view>
      </view>
    </view>

    <!-- 房屋基本概况 -->
    <view class="card">
      <view class="card-header"><text class="card-title">房屋基本概况</text></view>
      <view class="form-list">
        <view class="form-item"><text class="form-label">房屋名称</text><input v-model="form.buildingName" placeholder="房屋名称" class="form-input" /></view>
        <view class="form-item"><text class="form-label">房屋座落</text><input v-model="form.location" placeholder="房屋地址" class="form-input" /></view>
        <view class="form-item"><text class="form-label">街道</text><input v-model="form.street" placeholder="街道" class="form-input" /></view>
        <view class="form-item"><text class="form-label">社区</text><input v-model="form.community" placeholder="社区" class="form-input" /></view>
        <view class="form-item"><text class="form-label">产权人</text><input v-model="form.propertyOwner" placeholder="产权人" class="form-input" /></view>
        <view class="form-item"><text class="form-label">使用人</text><input v-model="form.propertyUser" placeholder="使用人" class="form-input" /></view>
        <view class="form-item"><text class="form-label">产权性质</text><input v-model="form.propertyNature" placeholder="产权性质" class="form-input" /></view>
        <view class="form-item"><text class="form-label">鉴定类别说明</text><input v-model="form.surveyCategoryDesc" placeholder="鉴定类别说明" class="form-input" /></view>
        <view class="form-item-row"><text class="form-label">产权证号</text><input v-model="form.certificateNo" placeholder="产权证号" class="form-input-flex" :disabled="form.certificateNoUnknown" /><view class="check-box" @click="form.certificateNoUnknown = !form.certificateNoUnknown"><view class="check-mark" :class="{ checked: form.certificateNoUnknown }"></view>不详</view></view>
        <view class="form-item-row"><text class="form-label">建成年份</text><input v-model="form.buildYear" placeholder="建成年份" class="form-input-flex" :disabled="form.buildYearUnknown" /><view class="check-box" @click="form.buildYearUnknown = !form.buildYearUnknown"><view class="check-mark" :class="{ checked: form.buildYearUnknown }"></view>不详</view></view>
        <view class="form-item"><text class="form-label">层数</text><input v-model="form.floorCount" type="number" placeholder="层数" class="form-input" /></view>
        <view class="form-item"><text class="form-label">层高(m)</text><input v-model="form.floorHeight" type="digit" placeholder="层高" class="form-input" /></view>
        <view class="form-item"><text class="form-label">总高(m)</text><input v-model="form.totalHeight" type="digit" placeholder="总高" class="form-input" /></view>
        <view class="form-item"><text class="form-label">檐口高度(m)</text><input v-model="form.eavesHeight" type="digit" placeholder="檐口高度" class="form-input" /></view>
        <view class="form-item"><text class="form-label">设计用途</text><input v-model="form.designUsage" placeholder="设计用途" class="form-input" /></view>
        <view class="form-item-row"><text class="form-label">原勘察单位</text><input v-model="form.originalSurveyUnit" placeholder="原勘察单位" class="form-input-flex" :disabled="form.originalSurveyUnitUnknown" /><view class="check-box" @click="form.originalSurveyUnitUnknown = !form.originalSurveyUnitUnknown"><view class="check-mark" :class="{ checked: form.originalSurveyUnitUnknown }"></view>不详</view></view>
        <view class="form-item-row"><text class="form-label">原设计单位</text><input v-model="form.originalDesignUnit" placeholder="原设计单位" class="form-input-flex" :disabled="form.originalDesignUnitUnknown" /><view class="check-box" @click="form.originalDesignUnitUnknown = !form.originalDesignUnitUnknown"><view class="check-mark" :class="{ checked: form.originalDesignUnitUnknown }"></view>不详</view></view>
        <view class="form-item-row"><text class="form-label">原施工单位</text><input v-model="form.originalConstructUnit" placeholder="原施工单位" class="form-input-flex" :disabled="form.originalConstructUnitUnknown" /><view class="check-box" @click="form.originalConstructUnitUnknown = !form.originalConstructUnitUnknown"><view class="check-mark" :class="{ checked: form.originalConstructUnitUnknown }"></view>不详</view></view>
        <view class="form-item-row"><text class="form-label">原监理单位</text><input v-model="form.originalSuperviseUnit" placeholder="原监理单位" class="form-input-flex" :disabled="form.originalSuperviseUnitUnknown" /><view class="check-box" @click="form.originalSuperviseUnitUnknown = !form.originalSuperviseUnitUnknown"><view class="check-mark" :class="{ checked: form.originalSuperviseUnitUnknown }"></view>不详</view></view>
      </view>
    </view>

    <!-- 用途信息 -->
    <view class="card">
      <view class="card-header"><text class="card-title">用途信息</text></view>
      <text class="section-label">原设计用途</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in purposeOptions" :key="'orig_'+opt" @click="toggleArray(form.originalPurpose, opt)"><view class="check-mark" :class="{ checked: form.originalPurpose.includes(opt) }"></view><text>{{ opt }}</text></view>
      </view>
      <view class="form-item" v-if="form.originalPurpose.includes('其他')"><text class="form-label">其他</text><input v-model="form.originalPurposeOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label" style="margin-top:20rpx;">现用途</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in currentPurposeOptions" :key="'cur_'+opt" @click="toggleArray(form.currentPurpose, opt)"><view class="check-mark" :class="{ checked: form.currentPurpose.includes(opt) }"></view><text>{{ opt }}</text></view>
      </view>
      <view class="form-item" v-if="form.currentPurpose.includes('其他')"><text class="form-label">其他</text><input v-model="form.currentPurposeOther" placeholder="请输入" class="form-input" /></view>
    </view>

    <!-- 结构构造信息 -->
    <view class="card">
      <view class="card-header"><text class="card-title">结构构造信息</text></view>
      <text class="section-label">地基处理</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in foundationTreatmentOpts" :key="opt" @click="toggleArray(form.foundationTreatment, opt)"><view class="check-mark" :class="{ checked: form.foundationTreatment.includes(opt) }"></view><text>{{ opt }}</text></view>
        <view class="check-box" @click="form.foundationTreatmentUnknown = !form.foundationTreatmentUnknown"><view class="check-mark" :class="{ checked: form.foundationTreatmentUnknown }"></view>不详</view>
      </view>
      <view class="form-item" v-if="form.foundationTreatment.includes('其他')"><text class="form-label">其他</text><input v-model="form.foundationTreatmentOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label">楼面型式</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in floorTypeOpts" :key="opt" @click="toggleArray(form.floorType, opt)"><view class="check-mark" :class="{ checked: form.floorType.includes(opt) }"></view><text>{{ opt }}</text></view>
        <view class="check-box" @click="form.floorTypeNone = !form.floorTypeNone"><view class="check-mark" :class="{ checked: form.floorTypeNone }"></view>无</view>
      </view>
      <view class="form-item" v-if="form.floorType.includes('其他')"><text class="form-label">其他</text><input v-model="form.floorTypeOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label">基础型式</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in foundationTypeOpts" :key="opt" @click="toggleArray(form.foundationType, opt)"><view class="check-mark" :class="{ checked: form.foundationType.includes(opt) }"></view><text>{{ opt }}</text></view>
        <view class="check-box" @click="form.foundationTypeUnknown = !form.foundationTypeUnknown"><view class="check-mark" :class="{ checked: form.foundationTypeUnknown }"></view>不详</view>
      </view>
      <view class="form-item" v-if="form.foundationType.includes('其他')"><text class="form-label">其他</text><input v-model="form.foundationTypeOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label">屋面构造</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in roofStructureOpts" :key="opt" @click="toggleArray(form.roofStructure, opt)"><view class="check-mark" :class="{ checked: form.roofStructure.includes(opt) }"></view><text>{{ opt }}</text></view>
      </view>
      <view class="form-item" v-if="form.roofStructure.includes('其他')"><text class="form-label">其他</text><input v-model="form.roofStructureOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label">墙体</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in wallTypeOpts" :key="opt" @click="toggleArray(form.wallType, opt)"><view class="check-mark" :class="{ checked: form.wallType.includes(opt) }"></view><text>{{ opt }}</text></view>
      </view>
      <view class="form-item" v-if="form.wallType.includes('其他')"><text class="form-label">其他</text><input v-model="form.wallTypeOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label">结构类型</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in structureTypeOpts" :key="opt" @click="toggleArray(form.structureTypes, opt)"><view class="check-mark" :class="{ checked: form.structureTypes.includes(opt) }"></view><text>{{ opt }}</text></view>
      </view>
      <view class="form-item" v-if="form.structureTypes.includes('其他')"><text class="form-label">其他</text><input v-model="form.structureTypeOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label">楼梯类型</text>
      <view class="check-group">
        <view class="check-item" v-for="opt in stairTypeOpts" :key="opt" @click="toggleArray(form.stairType, opt)"><view class="check-mark" :class="{ checked: form.stairType.includes(opt) }"></view><text>{{ opt }}</text></view>
        <view class="check-box" @click="form.stairTypeNone = !form.stairTypeNone"><view class="check-mark" :class="{ checked: form.stairTypeNone }"></view>无</view>
      </view>
      <view class="form-item" v-if="form.stairType.includes('其他')"><text class="form-label">其他</text><input v-model="form.stairTypeOther" placeholder="请输入" class="form-input" /></view>
      <text class="section-label">抗震设防</text>
      <view class="form-item"><text class="form-label">设防级别</text><input v-model="form.seismicLevel" placeholder="抗震设防级别" class="form-input" :disabled="form.seismicNone || form.seismicUnknown" /></view>
      <view style="display:flex;gap:30rpx;padding:10rpx 0;"><view class="check-box" @click="toggleSeismic('none')"><view class="check-mark" :class="{ checked: form.seismicNone }"></view>无</view><view class="check-box" @click="toggleSeismic('unknown')"><view class="check-mark" :class="{ checked: form.seismicUnknown }"></view>不详</view></view>
    </view>

    <!-- 历史变更 -->
    <view class="card">
      <view class="card-header"><text class="card-title">历史变更</text></view>
      <view class="radio-group" v-for="item in ynRadioItems" :key="'hc_'+item.key"><text class="radio-label">{{ item.label }}</text><view class="radio-options"><text class="radio-item" v-for="v in ynOptions" :key="v.value" @click="form[item.key] = v.value" :class="{ 'radio-active': form[item.key] === v.value }">{{ v.label }}</text></view></view>
    </view>

    <!-- 使用情况 -->
    <view class="card">
      <view class="card-header"><text class="card-title">使用情况</text></view>
      <view class="radio-group" v-for="item in usageRadioItems" :key="'us_'+item.key"><text class="radio-label">{{ item.label }}</text><view class="radio-options"><text class="radio-item" v-for="v in ynOptions" :key="v.value" @click="form[item.key] = v.value" :class="{ 'radio-active': form[item.key] === v.value }">{{ v.label }}</text></view></view>
    </view>

    <!-- 专项标识信息 -->
    <view class="card">
      <view class="card-header"><text class="card-title">专项标识信息</text></view>
      <view class="radio-group" v-for="item in selfBuiltRadioItems" :key="item.key">
        <text class="radio-label">{{ item.label }}</text>
        <view class="radio-options">
          <text class="radio-item" v-for="v in yesNoOptions" :key="v.label" @click="form[item.key] = v.value" :class="{ 'radio-active': form[item.key] === v.value }">{{ v.label }}</text>
        </view>
      </view>
      <view class="form-list" style="margin-top:16rpx;">
        <view class="form-item"><text class="form-label">自建房排查编码</text><input v-model="form.selfBuildingCheckCode" placeholder="排查编码" class="form-input" /></view>
        <view class="form-item"><text class="form-label">普查房屋编号</text><input v-model="form.censusHouseNo" placeholder="普查编号" class="form-input" /></view>
      </view>
    </view>

    <!-- 证件图纸资料 -->
    <view class="card">
      <view class="card-header"><text class="card-title">证件图纸资料</text></view>
      <view class="check-group">
        <view class="check-item" v-for="opt in clientMaterialOpts" :key="opt" @click="toggleArray(form.clientMaterials, opt)"><view class="check-mark" :class="{ checked: form.clientMaterials.includes(opt) }"></view><text>{{ opt }}</text></view>
      </view>
      <view class="form-item" v-if="form.clientMaterials.includes('其他')"><text class="form-label">其他</text><input v-model="form.clientMaterialsOther" placeholder="请输入" class="form-input" /></view>
    </view>

    <!-- 周边环境 -->
    <view class="card">
      <view class="card-header"><text class="card-title">周边环境</text></view>
      <view class="radio-options">
        <text class="radio-item" v-for="opt in surroundOptions" :key="opt.value" @click="form.surroundingEnvironment = opt.value" :class="{ 'radio-active': form.surroundingEnvironment === opt.value }">{{ opt.label }}</text>
      </view>
      <view class="form-item-block" v-if="form.surroundingEnvironment === 'deepExcavation' || form.surroundingEnvironment === 'other'"><text class="form-label">补充描述</text><textarea v-model="form.surroundingEnvironmentDesc" placeholder="请描述周边环境情况" class="form-textarea" /></view>
    </view>

    <!-- 文本描述 -->
    <view class="card">
      <view class="card-header"><text class="card-title">文本描述</text></view>
      <view class="form-list">
        <view class="form-item-block" v-for="item in textFields" :key="item.key">
          <view class="form-label-row"><text class="form-label">{{ item.label }}</text><view class="btn-row"><button class="btn-ai-mini" size="mini" :loading="aiLoading[item.key]" @click="generateText(item.key)">AI生成</button><button class="btn-clear" size="mini" @click="form[item.key] = ''">清空</button></view></view>
          <textarea v-model="form[item.key]" :placeholder="item.placeholder" class="form-textarea" />
        </view>
      </view>
    </view>

    <view class="save-section">
      <button class="btn-save" @click="handleSave">保存</button>
      <button class="btn-next" @click="handleSaveAndNext">保存并进入构件检查 →</button>
    </view>

    <!-- 快捷导航 -->
    <view class="quick-nav">
      <text class="quick-title">相关功能</text>
      <view class="quick-grid">
        <view class="quick-item" @click="goToDamageRecord"><text>构件检查</text></view>
		<view class="quick-item" @click="goTo('test-result-inference')"><text>检测结果推理</text></view>
        <view class="quick-item" @click="goTo('report-preview')"><text>鉴定报告预览</text></view>
        <view class="quick-item" @click="goTo('original-record')"><text>原始记录</text></view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getSurveyDetail, updateSurvey } from '@/api/survey.js'
import { generateUsageHistory, generateExternalEnvironment, generateStructureCondition, generateRemarks as generateRemarksAI, generateEvaluationStandards } from '@/api/ai.js'

const surveyId = ref('')
const form = reactive({
  surveyNo: '', surveyType: '整栋鉴定', surveyPurpose: '', surveyArea: '',
  clientUnit: '', clientName: '', contactPerson: '', contactPhone: '', surveyDate: '', inspectionDate: '',
  buildingName: '', location: '', street: '', community: '',
  propertyOwner: '', propertyUser: '', propertyNature: '', surveyCategoryDesc: '',
  certificateNo: '', certificateNoUnknown: false,
  buildYear: '', buildYearUnknown: false,
  floorCount: '', floorHeight: '', totalHeight: '', eavesHeight: '', designUsage: '',
  originalSurveyUnit: '', originalSurveyUnitUnknown: false,
  originalDesignUnit: '', originalDesignUnitUnknown: false,
  originalConstructUnit: '', originalConstructUnitUnknown: false,
  originalSuperviseUnit: '', originalSuperviseUnitUnknown: false,
  originalPurpose: [], originalPurposeOther: '',
  currentPurpose: [], currentPurposeOther: '',
  foundationTreatment: [], foundationTreatmentOther: '', foundationTreatmentUnknown: false,
  floorType: [], floorTypeOther: '', floorTypeNone: false,
  foundationType: [], foundationTypeOther: '', foundationTypeUnknown: false,
  roofStructure: [], roofStructureOther: '',
  wallType: [], wallTypeOther: '',
  structureTypes: [], structureTypeOther: '',
  stairType: [], stairTypeOther: '', stairTypeNone: false,
  seismicLevel: '', seismicNone: false, seismicUnknown: false,
  purposeChange: 'unknown', renovation: 'unknown', reinforcement: 'unknown', disaster: 'unknown',
  structureModification: 'unknown', illegalConstruction: 'unknown', overloadUsage: 'unknown', otherUsage: 'unknown',
  isCulturalRelic: false, isRuralRenovation: false, isTrainingInstitution: false,
  isSelfBuiltReport: false, isSelfBuilt: false, isCommercialSelfBuilt: false,
  isRuralDangerousRepair: false, isProtectedBuilding: false, isHistoricalCertificate: false,
  selfBuildingCheckCode: '', censusHouseNo: '',
  clientMaterials: [], clientMaterialsOther: '',
  surroundingEnvironment: '', surroundingEnvironmentDesc: '',
  usageHistory: '', externalEnvironment: '', structureCondition: '', evaluationStandards: '', remarks: ''
})

const aiLoading = reactive({ usageHistory: false, externalEnvironment: false, structureCondition: false })

const surveyTypeOptions = ['整栋鉴定', '局部鉴定']
const purposeOptions = ['住宅', '宿舍', '办公', '商业用房', '综合楼', '工业厂房', '仓库', '医院', '教学楼', '幼儿园', '商店', '剧场', '礼堂', '其他']
const currentPurposeOptions = [...purposeOptions, '空置']
const foundationTreatmentOpts = ['换填垫层', '粉喷桩复合地基', '其他']
const floorTypeOpts = ['预制圆孔板', '现浇钢筋砼板', '木楼面', '钢楼层板', '其他']
const foundationTypeOpts = ['桩基础', '柱下独立柱基', '条形基础', '其他']
const roofStructureOpts = ['预制圆孔板', '现浇钢筋砼板', '红瓦', '石棉瓦', '压型钢板', '其他']
const wallTypeOpts = ['红砖', '砌块', '框架填充墙', '板条墙', '压型钢板', '其他']
const structureTypeOpts = ['混合', '框架', '砖木', '框肢剪力墙', '排架', '门式钢架', '框筒', '其他']
const stairTypeOpts = ['钢筋砼楼梯', '钢楼梯', '木楼梯', '其他']
const clientMaterialOpts = ['产权证复印件', '地质勘察报告', '改造扩建资料', '场区总平面图', '基坑支护方案', '加固修缮资料', '设计施竣工图', '质检验收资料', '变形监测资料', '其他']
const ynOptions = [{ label: '有', value: 'has' }, { label: '无', value: 'none' }, { label: '不详', value: 'unknown' }]
const ynRadioItems = [{ key: 'purposeChange', label: '用途变更' }, { key: 'renovation', label: '改造扩建' }, { key: 'reinforcement', label: '加固修缮' }, { key: 'disaster', label: '自然灾害' }]
const usageRadioItems = [{ key: 'structureModification', label: '拆改结构' }, { key: 'illegalConstruction', label: '乱搭乱盖' }, { key: 'overloadUsage', label: '超载使用' }, { key: 'otherUsage', label: '其他' }]
const yesNoOptions = [{ label: '是', value: true }, { label: '否', value: false }]
const selfBuiltRadioItems = [
  { key: "isCulturalRelic", label: "是否优保（文保）建筑" },
  { key: "isRuralRenovation", label: "是否农村危房改造" },
  { key: "isRuralDangerousRepair", label: "是否农村危房改造（新）" },
  { key: "isTrainingInstitution", label: "是否校外培训机构" },
  { key: "isSelfBuiltReport", label: "是否自建房专项鉴定报告" },
  { key: "isSelfBuilt", label: "是否自建房" },
  { key: "isCommercialSelfBuilt", label: "是否经营性自建房" },
  { key: "isHistoricalCertificate", label: "是否历史遗留办证" },
]
const surroundOptions = [
  { label: '正常，查勘时该房屋周边无建设施工', value: 'normal' },
  { label: '距该房屋侧约米处进行深基坑施工', value: 'deepExcavation' },
  { label: '其他', value: 'other' }
]
const textFields = [
  { key: 'usageHistory', label: '使用历史', placeholder: '房屋使用、维修改造、灾害等历史情况' },
  { key: 'externalEnvironment', label: '外部环境', placeholder: '房屋外部环境及周边建设施工情况' },
  { key: 'structureCondition', label: '结构状况', placeholder: '房屋地质勘察、地基基础、主体结构及其他情况' },
  { key: 'evaluationStandards', label: '鉴定依据标准', placeholder: '本鉴定依据标准及规范' },
  { key: 'remarks', label: '备注', placeholder: '备注' }
]

const toggleArray = (arr, val) => { const i = arr.indexOf(val); i > -1 ? arr.splice(i, 1) : arr.push(val) }
const toggleSeismic = (type) => { if (type === 'none') { form.seismicNone = !form.seismicNone; if (form.seismicNone) form.seismicUnknown = false } else { form.seismicUnknown = !form.seismicUnknown; if (form.seismicUnknown) form.seismicNone = false } }

onMounted(() => { const pages = getCurrentPages(); const cp = pages[pages.length - 1]; surveyId.value = cp.options.id || ''; loadSurveyDetail() })

const goToDamageRecord = () => { uni.navigateTo({ url: `/pages/damage-record/damage-record?id=${surveyId.value}` }) }
const goTo = (page) => { uni.navigateTo({ url: `/pages/${page}/${page}?id=${surveyId.value}` }) }

const loadSurveyDetail = async () => {
  try {
    const res = await getSurveyDetail(surveyId.value)
    if (!res) return
    // Map backend snake_case fields to form fields
    form.surveyNo = res.survey_no || res.surveyNo || ''
    form.surveyType = res.survey_category || res.surveyType || '整栋鉴定'
    form.surveyPurpose = res.survey_purpose || res.surveyPurpose || ''
    form.surveyArea = res.build_area || res.surveyArea || ''
    form.clientName = res.client_name || res.clientName || ''
    form.contactPerson = res.contact_person || res.contactPerson || ''
    form.contactPhone = res.contact_phone || res.contactPhone || ''
    form.surveyDate = res.survey_date || res.surveyDate || ''
    form.inspectionDate = res.inspection_complete_date || res.inspectionDate || ''
    form.buildingName = res.house_name || res.buildingName || ''
    form.location = res.address || res.location || ''
    form.street = res.street || ''
    form.community = res.community || ''
    form.propertyOwner = res.property_owner || res.propertyOwner || ''
    form.propertyUser = res.property_user || res.propertyUser || ''
    form.propertyNature = res.property_nature || res.propertyNature || ''
    form.surveyCategoryDesc = res.survey_category_desc || res.surveyCategoryDesc || ''
    form.certificateNo = res.property_certificate_no || res.certificateNo || ''
    form.buildYear = res.build_year || res.buildYear || ''
    form.floorCount = res.floor_count || res.floorCount || ''
    form.totalHeight = res.building_height || res.totalHeight || ''
    form.eavesHeight = res.eaves_height || res.eavesHeight || ''
    form.designUsage = res.design_usage || res.designUsage || ''
    form.originalDesignUnit = res.design_unit || res.originalDesignUnit || ''
    form.originalConstructUnit = res.construction_unit || res.originalConstructUnit || ''
    form.originalSuperviseUnit = res.supervision_unit || res.originalSuperviseUnit || ''
    form.selfBuildingCheckCode = res.self_building_check_code || res.selfBuildingCheckCode || ''
    form.censusHouseNo = res.census_house_no || res.censusHouseNo || ''
    form.usageHistory = res.usage_history || res.usageHistory || ''
    form.externalEnvironment = res.external_environment || res.externalEnvironment || ''
    form.evaluationStandards = res.evaluation_standards || res.evaluationStandards || ''
    form.remarks = res.remark || res.remarks || ''
    form.isRuralDangerousRepair = res.is_rural_dangerous_repair ?? form.isRuralDangerousRepair
    form.isProtectedBuilding = res.is_protected_building ?? form.isProtectedBuilding
    form.isHistoricalCertificate = res.is_historical_certificate ?? form.isHistoricalCertificate
    form.isTrainingInstitution = res.is_training_institution ?? form.isTrainingInstitution
    form.isSelfBuiltReport = res.is_self_building_special_report ?? form.isSelfBuiltReport
    form.isSelfBuilt = res.is_self_building ?? form.isSelfBuilt
    form.isCommercialSelfBuilt = res.is_commercial_self_building ?? form.isCommercialSelfBuilt
    // Load building_profile sub-objects
    const bp = res.building_profile || res.buildingProfile
    if (bp) {
      if (bp.basicInfo) {
        const bi = bp.basicInfo
        if (bi.buildingName) form.buildingName = bi.buildingName
        if (bi.location) form.location = bi.location
        if (bi.floorCount) form.floorCount = bi.floorCount
        if (bi.floorHeight) form.floorHeight = bi.floorHeight
        if (bi.totalHeight) form.totalHeight = bi.totalHeight
        if (bi.buildArea) form.surveyArea = bi.buildArea
        if (bi.buildYear) form.buildYear = bi.buildYear
        if (bi.buildYearUnknown !== undefined) form.buildYearUnknown = bi.buildYearUnknown
        if (bi.propertyRight) form.propertyNature = bi.propertyRight
        if (bi.certificateNo) form.certificateNo = bi.certificateNo
        if (bi.certificateNoUnknown !== undefined) form.certificateNoUnknown = bi.certificateNoUnknown
        if (bi.originalSurveyUnit) form.originalSurveyUnit = bi.originalSurveyUnit
        if (bi.originalSurveyUnitUnknown !== undefined) form.originalSurveyUnitUnknown = bi.originalSurveyUnitUnknown
        if (bi.originalDesignUnit) form.originalDesignUnit = bi.originalDesignUnit
        if (bi.originalDesignUnitUnknown !== undefined) form.originalDesignUnitUnknown = bi.originalDesignUnitUnknown
        if (bi.originalConstructUnit) form.originalConstructUnit = bi.originalConstructUnit
        if (bi.originalConstructUnitUnknown !== undefined) form.originalConstructUnitUnknown = bi.originalConstructUnitUnknown
        if (bi.originalSuperviseUnit) form.originalSuperviseUnit = bi.originalSuperviseUnit
        if (bi.originalSuperviseUnitUnknown !== undefined) form.originalSuperviseUnitUnknown = bi.originalSuperviseUnitUnknown
      }
      if (bp.clientInfo) {
        const ci = bp.clientInfo
        if (ci.clientUnit) form.clientUnit = ci.clientUnit
        if (ci.clientName) form.clientName = ci.clientName
        if (ci.contactPerson) form.contactPerson = ci.contactPerson
        if (ci.contactPhone) form.contactPhone = ci.contactPhone
      }
      if (bp.purposeInfo) Object.keys(bp.purposeInfo).forEach(k => { if (bp.purposeInfo[k] !== undefined) form[k] = bp.purposeInfo[k] })
      if (bp.structureInfo) Object.keys(bp.structureInfo).forEach(k => { if (bp.structureInfo[k] !== undefined) form[k] = bp.structureInfo[k] })
      if (bp.historyChange) Object.keys(bp.historyChange).forEach(k => { if (bp.historyChange[k] !== undefined) form[k] = bp.historyChange[k] })
      if (bp.usageStatus) Object.keys(bp.usageStatus).forEach(k => { if (bp.usageStatus[k] !== undefined) form[k] = bp.usageStatus[k] })
      if (bp.selfBuiltInfo) Object.keys(bp.selfBuiltInfo).forEach(k => { if (bp.selfBuiltInfo[k] !== undefined) form[k] = bp.selfBuiltInfo[k] })
      if (bp.textDescription) { ['clientMaterials','clientMaterialsOther','surroundingEnvironment','surroundingEnvironmentDesc','usageHistory','externalEnvironment','structureCondition','remarks'].forEach(k => { if (bp.textDescription[k] !== undefined) form[k] = bp.textDescription[k] }) }
    }

  } catch (e) { console.error(e) }
}

const generateText = async (type) => {
  aiLoading[type] = true
  try {
    const ynMap = { has: '有', none: '无', unknown: '不详' }
    let res
    switch (type) {
      case 'usageHistory': {
        const historyChange = ynRadioItems.map(item =>
          `${item.label}: ${ynMap[form[item.key]] || form[item.key]}`
        ).join('; ')
        const usageStatus = usageRadioItems.map(item =>
          `${item.label}: ${ynMap[form[item.key]] || form[item.key]}`
        ).join('; ')
        const purposeInfo = `现用途: ${(form.currentPurpose || []).join(', ') || '不详'}`
        res = await generateUsageHistory(historyChange, usageStatus, purposeInfo)
        form.usageHistory = res.content || ''
        break
      }
      case 'externalEnvironment': {
        res = await generateExternalEnvironment('', form.street + form.community)
        form.externalEnvironment = res.content || ''
        break
      }
      case 'structureCondition': {
        const structureInfo = [
          `结构类型: ${(form.structureTypes || []).join(', ') || '不详'}`,
          `地基处理: ${(form.foundationTreatment || []).join(', ') || '不详'}`,
          `基础型式: ${(form.foundationType || []).join(', ') || '不详'}`,
          `楼面型式: ${(form.floorType || []).join(', ') || '不详'}`,
          `屋面构造: ${(form.roofStructure || []).join(', ') || '不详'}`,
          `墙体: ${(form.wallType || []).join(', ') || '不详'}`,
          `楼梯类型: ${(form.stairType || []).join(', ') || '不详'}`,
          `抗震设防: ${form.seismicLevel || '不详'}`,
        ].join('; ')
        const basicInfo = `层数: ${form.floorCount}, 建成年份: ${form.buildYear}, 面积: ${form.surveyArea}`
        res = await generateStructureCondition(structureInfo, basicInfo)
        form.structureCondition = res.content || ''
        break
      }
      case 'evaluationStandards': {
        const buildingInfo = [
          `结构类型: ${(form.structureTypes || []).join(', ') || '不详'}`,
          `层数: ${form.floorCount}`,
          `建成年份: ${form.buildYear}`,
          `面积: ${form.surveyArea}㎡`,
          `基础型式: ${(form.foundationType || []).join(', ') || '不详'}`,
        ].join('; ')
        res = await generateEvaluationStandards(buildingInfo)
        form.evaluationStandards = res.content || ''
        break
      }
      case 'remarks': {
        res = await generateRemarksAI()
        form.remarks = res.content || ''
        break
      }
    }
  } catch (e) { console.error(e) } finally { aiLoading[type] = false }
}

const handleSave = async () => {
  try {
    const bp = {
      basicInfo: {
        buildingName: form.buildingName, location: form.location,
        floorCount: form.floorCount, floorHeight: form.floorHeight,
        totalHeight: form.totalHeight, buildArea: form.surveyArea,
        buildYear: form.buildYearUnknown ? '不详' : form.buildYear,
        buildYearUnknown: form.buildYearUnknown,
        propertyRight: form.propertyNature,
        propertyRightUnknown: false,
        certificateNo: form.certificateNoUnknown ? '不详' : form.certificateNo,
        certificateNoUnknown: form.certificateNoUnknown,
        originalSurveyUnit: form.originalSurveyUnitUnknown ? '不详' : form.originalSurveyUnit,
        originalSurveyUnitUnknown: form.originalSurveyUnitUnknown,
        originalDesignUnit: form.originalDesignUnitUnknown ? '不详' : form.originalDesignUnit,
        originalDesignUnitUnknown: form.originalDesignUnitUnknown,
        originalConstructUnit: form.originalConstructUnitUnknown ? '不详' : form.originalConstructUnit,
        originalConstructUnitUnknown: form.originalConstructUnitUnknown,
        originalSuperviseUnit: form.originalSuperviseUnitUnknown ? '不详' : form.originalSuperviseUnit,
        originalSuperviseUnitUnknown: form.originalSuperviseUnitUnknown,
      },
      clientInfo: {
        clientUnit: form.clientUnit, clientName: form.clientName,
        contactPerson: form.contactPerson, contactPhone: form.contactPhone,
      },
      purposeInfo: { originalPurpose: form.originalPurpose, originalPurposeOther: form.originalPurposeOther, currentPurpose: form.currentPurpose, currentPurposeOther: form.currentPurposeOther },
      structureInfo: { foundationTreatment: form.foundationTreatment, foundationTreatmentOther: form.foundationTreatmentOther, foundationTreatmentUnknown: form.foundationTreatmentUnknown, floorType: form.floorType, floorTypeOther: form.floorTypeOther, floorTypeNone: form.floorTypeNone, foundationType: form.foundationType, foundationTypeOther: form.foundationTypeOther, foundationTypeUnknown: form.foundationTypeUnknown, roofStructure: form.roofStructure, roofStructureOther: form.roofStructureOther, wallType: form.wallType, wallTypeOther: form.wallTypeOther, structureType: form.structureTypes, structureTypeOther: form.structureTypeOther, stairType: form.stairType, stairTypeOther: form.stairTypeOther, stairTypeNone: form.stairTypeNone, seismicLevel: form.seismicLevel, seismicNone: form.seismicNone, seismicUnknown: form.seismicUnknown },
      historyChange: { purposeChange: form.purposeChange, renovation: form.renovation, reinforcement: form.reinforcement, disaster: form.disaster },
      usageStatus: { structureModification: form.structureModification, illegalConstruction: form.illegalConstruction, overloadUsage: form.overloadUsage, other: form.otherUsage },
      selfBuiltInfo: { isCulturalRelic: form.isCulturalRelic, isRuralRenovation: form.isRuralRenovation, isTrainingInstitution: form.isTrainingInstitution, isSelfBuiltReport: form.isSelfBuiltReport, isSelfBuilt: form.isSelfBuilt, isCommercialSelfBuilt: form.isCommercialSelfBuilt, isRuralDangerousRepair: form.isRuralDangerousRepair, isProtectedBuilding: form.isProtectedBuilding, isHistoricalCertificate: form.isHistoricalCertificate, selfBuiltCheckCode: form.selfBuildingCheckCode, censusHouseNo: form.censusHouseNo },
      textDescription: { clientMaterials: form.clientMaterials, clientMaterialsOther: form.clientMaterialsOther, surroundingEnvironment: form.surroundingEnvironment, surroundingEnvironmentDesc: form.surroundingEnvironmentDesc, usageHistory: form.usageHistory, externalEnvironment: form.externalEnvironment, structureCondition: form.structureCondition, remarks: form.remarks }
    }
    await updateSurvey(surveyId.value, {
      survey_no: form.surveyNo,
      survey_category: form.surveyType,
      survey_purpose: form.surveyPurpose,
      build_area: form.surveyArea || null,
      client_name: form.clientName,
      contact_person: form.contactPerson,
      contact_phone: form.contactPhone,
      survey_date: form.surveyDate || null,
      inspection_complete_date: form.inspectionDate || null,
      house_name: form.buildingName,
      address: form.location,
      street: form.street,
      community: form.community,
      property_owner: form.propertyOwner,
      property_user: form.propertyUser,
      property_nature: form.propertyNature,
      survey_category_desc: form.surveyCategoryDesc,
      property_certificate_no: form.certificateNoUnknown ? '不详' : form.certificateNo,
      build_year: form.buildYearUnknown ? '不详' : form.buildYear,
      floor_count: form.floorCount || null,
      building_height: form.totalHeight || null,
      eaves_height: form.eavesHeight,
      design_usage: form.designUsage,
      design_unit: form.originalDesignUnitUnknown ? '不详' : form.originalDesignUnit,
      construction_unit: form.originalConstructUnitUnknown ? '不详' : form.originalConstructUnit,
      supervision_unit: form.originalSuperviseUnitUnknown ? '不详' : form.originalSuperviseUnit,
      self_building_check_code: form.selfBuildingCheckCode,
      census_house_no: form.censusHouseNo,
      usage_history: form.usageHistory,
      external_environment: form.externalEnvironment,
      evaluation_standards: form.evaluationStandards,
      remark: form.remarks,
      is_rural_dangerous_repair: form.isRuralDangerousRepair,
      is_protected_building: form.isProtectedBuilding,
      is_historical_certificate: form.isHistoricalCertificate,
      is_training_institution: form.isTrainingInstitution,
      is_self_building_special_report: form.isSelfBuiltReport,
      is_self_building: form.isSelfBuilt,
      is_commercial_self_building: form.isCommercialSelfBuilt,
      building_profile: bp,
    })
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (e) { console.error(e); uni.showToast({ title: '保存失败', icon: 'none' }) }
}
const handleSaveAndNext = async () => {
  await handleSave()
  setTimeout(() => { goToDamageRecord() }, 500)
}
</script>

<style scoped>
.container { padding: 20rpx; padding-bottom: 140rpx; }
.step-nav { display: flex; align-items: center; gap: 12rpx; padding: 16rpx 20rpx; margin-bottom: 16rpx; background: #fff; border-radius: 4rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,.01); }
.step { display: flex; align-items: center; gap: 8rpx; }
.step.active .step-num { background: #226CB3; color: #fff; }
.step-num { width: 40rpx; height: 40rpx; border-radius: 50%; background: #DBDFE4; color: #626F7D; font-size: 24rpx; display: flex; align-items: center; justify-content: center; }
.step.active .step-text { color: #171D26; font-weight: bold; }
.step-text { font-size: 24rpx; color: #626F7D; }
.step-arrow { font-size: 22rpx; color: #226CB3; }
.step-divider { flex: 1; height: 2rpx; background: #DBDFE4; }
.step-link { background: #E3EDF6; border-radius: 4rpx; padding: 8rpx 16rpx; }
.btn-inspect-entry { width: 100%; background: #226CB3; color: #fff; border: none; border-radius: 4rpx; padding: 24rpx 0; font-size: 32rpx; margin-bottom: 20rpx; }
.card { background-color: #fff; border-radius: 4rpx; padding: 24rpx; margin-bottom: 20rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,.02); }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20rpx; padding-bottom: 16rpx; border-bottom: 1rpx solid #DBDFE4; }
.card-title { font-size: 32rpx; font-weight: bold; color: #171D26; }
.section-label { display: block; font-size: 26rpx; color: #454D59; font-weight: bold; margin: 16rpx 0 8rpx 0; }
.form-list { padding: 10rpx 0; }
.form-item { display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx dashed #DBDFE4; }
.form-item:last-child { border-bottom: none; }
.form-item-row { display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx dashed #DBDFE4; flex-wrap: wrap; }
.form-item-block { padding: 20rpx 0; border-bottom: 1rpx dashed #DBDFE4; }
.form-item-block:last-child { border-bottom: none; }
.form-label { width: 160rpx; font-size: 28rpx; color: #626F7D; flex-shrink: 0; }
.form-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12rpx; }
.form-input { flex: 1; height: 60rpx; padding: 0 20rpx; font-size: 28rpx; background-color: #EDF0F4; border-radius: 4rpx; }
.form-input-flex { flex: 1; height: 60rpx; padding: 0 20rpx; font-size: 26rpx; background-color: #EDF0F4; border-radius: 4rpx; min-width: 120rpx; }
.form-textarea { width: 100%; height: 160rpx; padding: 16rpx; font-size: 26rpx; background-color: #EDF0F4; border-radius: 4rpx; box-sizing: border-box; }
.picker-value { flex: 1; height: 60rpx; line-height: 60rpx; padding: 0 20rpx; font-size: 28rpx; background: #EDF0F4; border-radius: 4rpx; color: #454D59; }
.btn-ai-mini { background-color: #E28A13; color: #fff; border: none; border-radius: 4rpx; padding: 8rpx 20rpx; font-size: 22rpx; }
.btn-row { display: flex; gap: 12rpx; }
.btn-clear { background-color: #DBDFE4; color: #626F7D; border: none; border-radius: 4rpx; padding: 8rpx 20rpx; font-size: 22rpx; }
.check-group { display: flex; flex-wrap: wrap; gap: 12rpx; }
.check-item { display: flex; align-items: center; gap: 8rpx; padding: 8rpx 16rpx; background-color: #EDF0F4; border-radius: 4rpx; font-size: 26rpx; color: #454D59; }
.check-mark { width: 34rpx; height: 34rpx; border: 3rpx solid #226CB3; border-radius: 4rpx; background: #fff; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; box-sizing: border-box; }
.check-mark.checked { background: #226CB3; border-color: #226CB3; position: relative; }
.check-mark.checked::after { content: ''; position: absolute; left: 8rpx; top: 4rpx; width: 12rpx; height: 20rpx; border: solid #fff; border-width: 0 4rpx 4rpx 0; transform: rotate(45deg); }
.check-box { font-size: 24rpx; color: #626F7D; white-space: nowrap; padding: 8rpx 12rpx; display: inline-flex; align-items: center; gap: 6rpx; }
.radio-group { display: flex; align-items: center; justify-content: space-between; padding: 16rpx 0; border-bottom: 1rpx dashed #DBDFE4; }
.radio-group:last-child { border-bottom: none; }
.radio-label { font-size: 28rpx; color: #171D26; width: 160rpx; }
.radio-options { display: flex; gap: 12rpx; }
.radio-item { font-size: 24rpx; padding: 8rpx 24rpx; border-radius: 4rpx; background-color: #EDF0F4; color: #626F7D; }
.radio-active { background-color: #226CB3; color: #fff; }
.save-section { position: fixed; bottom: 0; left: 0; right: 0; padding: 20rpx; background: #fff; box-shadow: 0 -2rpx 12rpx rgba(0,0,0,.03); display: flex; gap: 16rpx; }
.btn-save { flex: 1; background-color: #EDF0F4; color: #454D59; border: none; border-radius: 4rpx; padding: 24rpx 0; font-size: 28rpx; }
.btn-next { flex: 2; background-color: #226CB3; color: #fff; border: none; border-radius: 4rpx; padding: 24rpx 0; font-size: 30rpx; }
.quick-nav { padding: 20rpx; margin-bottom: 40rpx; }
.quick-title { font-size: 26rpx; color: #626F7D; margin-bottom: 16rpx; display: block; }
.quick-grid { display: flex; flex-wrap: wrap; gap: 12rpx; }
.quick-item { padding: 14rpx 24rpx; background: #E3EDF6; border-radius: 4rpx; font-size: 26rpx; color: #226CB3; }
</style>
