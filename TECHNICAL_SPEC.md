# 房屋安全鉴定小程序 - 完整技术规范文档

## 1. 项目概述

### 1.1 应用定位
为建筑设计院专业鉴定人员设计的房屋安全鉴定数据采集和报告生成系统，支持AI辅助推理和报告生成。

### 1.2 技术栈总览

| 层级 | 技术选型 | 版本 |
|------|----------|------|
| 前端框架 | React + TypeScript | React 19 |
| 路由 | React Router DOM | v6 |
| 状态管理 | React Hooks + React Query | - |
| 表单管理 | React Hook Form + Zod | - |
| UI组件库 | shadcn/ui (基于Radix UI) | - |
| 样式方案 | Tailwind CSS + styled-jsx | - |
| 后端框架 | NestJS + TypeScript | v10.x |
| 数据库 | PostgreSQL + Drizzle ORM | - |
| AI能力 | 平台内置AI插件 | - |
| 文件存储 | 平台Dataloom存储 | - |

---

## 2. 项目目录结构

```
├── client/                     # React前端
│   ├── src/
│   │   ├── api/               # API层
│   │   │   ├── index.ts
│   │   │   ├── survey.ts
│   │   │   ├── damage-component.ts
│   │   │   ├── report.ts
│   │   │   ├── original-record.ts
│   │   │   ├── ai-plugin.ts
│   │   │   ├── structural-test-result.ts
│   │   │   ├── report-signature.ts
│   │   │   └── test-image.ts
│   │   ├── components/
│   │   │   ├── ui/            # shadcn/ui组件
│   │   │   ├── business-ui/   # 业务组件
│   │   │   └── Layout.tsx
│   │   ├── pages/
│   │   │   ├── SurveyList/
│   │   │   ├── DataCollection/
│   │   │   ├── ReportPreview/
│   │   │   ├── OriginalRecordPreview/
│   │   │   ├── AIAssistant/
│   │   │   ├── Login/
│   │   │   └── NotFound/
│   │   ├── app.tsx
│   │   └── index.tsx
├── server/                     # NestJS后端
│   ├── modules/
│   │   ├── survey/
│   │   ├── damage-component/
│   │   ├── report/
│   │   ├── original-record/
│   │   ├── ai-text-generation/
│   │   ├── structural-test-result/
│   │   ├── report-signature/
│   │   └── test-image/
│   ├── database/
│   │   └── schema.ts
│   ├── capabilities/          # 插件配置
│   └── app.module.ts
└── shared/                     # 前后端共享
    └── api.interface.ts
```

---

## 3. 页面功能详细规格

### 3.1 鉴定列表页 (SurveyList)

**文件路径**: `/client/src/pages/SurveyList/SurveyList.tsx`

**功能描述**:
- 展示所有鉴定记录列表
- 支持按地址、房屋名称、委托人搜索
- 支持分页浏览
- 创建新鉴定记录
- 删除鉴定记录（确认弹窗）
- 点击进入数据采集页

**状态管理**:
```typescript
// 使用React Query获取数据
const { data, isLoading } = useQuery({
  queryKey: ['surveys', page, pageSize, searchKeyword],
  queryFn: () => getSurveyList({ page, pageSize, keyword: searchKeyword }),
});

// 本地状态
const [searchKeyword, setSearchKeyword] = useState('');
const [page, setPage] = useState(1);
const [pageSize] = useState(10);
const [createDialogOpen, setCreateDialogOpen] = useState(false);
```

**API调用**:
```typescript
// 获取列表
GET /api/surveys?page=1&pageSize=10&keyword=xxx

// 创建鉴定
POST /api/surveys
{ address: string }

// 删除鉴定
DELETE /api/surveys/:id
```

**UI组件**:
- Card - 列表容器
- Input - 搜索框
- Button - 操作按钮
- Dialog - 创建弹窗
- Table/Antd Table - 数据列表
- Pagination - 分页

---

### 3.2 数据采集主页面 (DataCollection)

**文件路径**: `/client/src/pages/DataCollection/DataCollection.tsx`

**功能描述**:
- 多步骤数据采集流程
- 整合房屋概况、损坏构件、结构检测、签章信息等多个子表单
- 支持AI推理一键生成鉴定结论
- 实时预览生成的报告
- 自动保存草稿
- 提交完成鉴定

**页面结构**:
```
DataCollection (主页面)
├── Tabs导航
│   ├── 房屋概况 → BuildingProfileForm
│   ├── 损坏构件 → DamageComponentList + DamageComponentDialog
│   ├── 结构检测 → StructuralTestResultForm
│   ├── 签章信息 → ReportSignatureForm
│   ├── 检测图片 → TestImageForm
│   └── 报告数据 → ReportDataForm
├── 底部操作栏
│   ├── AI推理按钮
│   ├── 保存草稿按钮
│   ├── 预览报告按钮
│   └── 提交按钮
└── 侧边预览面板 → ReportPreviewPanel
```

**状态管理**:
```typescript
// 当前激活的Tab
const [activeTab, setActiveTab] = useState('profile');

// 加载状态
const [loading, setLoading] = useState(false);
const [aiLoading, setAiLoading] = useState(false);

// 数据状态
const [survey, setSurvey] = useState<Survey | null>(null);
const [componentChecks, setComponentChecks] = useState<ComponentCheck[]>([]);
const [buildingProfile, setBuildingProfile] = useState<BuildingProfile | null>(null);

// 预览面板状态
const [previewOpen, setPreviewOpen] = useState(false);
```

**核心方法**:
```typescript
// 加载所有数据
const fetchData = async () => {
  const [surveyData, checksData] = await Promise.all([
    surveyApi.getSurveyById(id),
    componentCheckApi.getComponentCheckList(id),
  ]);
  setSurvey(surveyData);
  setComponentChecks(checksData.items);
  setBuildingProfile(surveyData.buildingProfile || null);
};

// AI推理
const handleAIReasoning = async () => {
  setAiLoading(true);
  const result = await callHousingSafetyAI({
    buildingInfo: extractBuildingInfo(buildingProfile),
    componentChecks: componentChecks,
  });
  // 更新鉴定结论和基础评定
  await updateSurvey({
    conclusion: result.conclusion,
    basicEvaluation: result.basicEvaluation,
    aiReasoningResult: result,
  });
  setAiLoading(false);
};
```

**API调用**:
```typescript
// 获取鉴定详情
GET /api/surveys/:id

// 获取构件检查列表
GET /api/surveys/:id/component-checks

// 更新鉴定
PUT /api/surveys/:id

// AI推理
调用 ai-plugin.ts 中的 callHousingSafetyAI
```

---

### 3.3 房屋概况编辑表单 (BuildingProfileForm)

**文件路径**: `/client/src/pages/DataCollection/BuildingProfileForm.tsx`

**功能描述**:
- 12个分组的房屋概况信息录入
- 支持AI辅助生成文本描述
- 表单验证和错误提示
- 自动保存到父组件

**12个字段分组**:

| 分组 | 字段 | 组件类型 |
|------|------|----------|
| 1.委托信息 | clientName, clientUnit, contactPerson, contactPhone | Input |
| 2.房屋基本概况 | buildingName, surveyType, location, propertyRight, buildArea, totalHeight, certificateNo, buildYear, floorHeight, floorCount | Input/Number |
| 3.原参建单位 | originalSurveyUnit, originalDesignUnit, originalConstructUnit, originalSuperviseUnit | Input + Checkbox(不详) |
| 4.房屋基本概况扩展 | propertyNature, propertyCertificateNo, eavesHeight | Input |
| 5.用途信息 | originalPurpose, currentPurpose | CheckboxGroup |
| 6.结构信息 | structureType, foundationType, foundationTreatment, wallType, floorType, roofStructure, stairType, seismicLevel | CheckboxGroup/Select |
| 7.历史变更 | purposeChange, renovation, reinforcement, disaster | RadioGroup |
| 8.使用状况 | structureModification, illegalConstruction, overloadUsage, other | RadioGroup |
| 9.专项标识信息 | isCulturalRelic, isRuralRenovation, isTrainingInstitution, isSelfBuiltReport, isSelfBuilt, isCommercialSelfBuilt, isRuralDangerousRepair, isProtectedBuilding, isHistoricalCertificate | RadioGroup |
| 10.证件图纸资料 | clientMaterials | CheckboxGroup |
| 11.周边环境 | surroundingEnvironment | RadioGroup + Input |
| 12.文本描述 | usageHistory, externalEnvironment, structureCondition, remarks | Textarea/TiptapEditor |

**表单Schema (Zod)**:
```typescript
const buildingProfileSchema = z.object({
  // 委托信息
  clientName: z.string().optional(),
  clientUnit: z.string().optional(),
  contactPerson: z.string().optional(),
  contactPhone: z.string().optional(),
  
  // 房屋基本概况
  buildingName: z.string().optional(),
  surveyType: z.string().optional(),
  location: z.string().optional(),
  propertyRight: z.string().optional(),
  buildArea: z.number().optional(),
  totalHeight: z.number().optional(),
  certificateNo: z.string().optional(),
  buildYear: z.string().optional(),
  floorHeight: z.number().optional(),
  floorCount: z.number().optional(),
  
  // 原参建单位 + 不详标记
  originalSurveyUnit: z.string().optional(),
  originalSurveyUnitUnknown: z.boolean().default(false),
  originalDesignUnit: z.string().optional(),
  originalDesignUnitUnknown: z.boolean().default(false),
  originalConstructUnit: z.string().optional(),
  originalConstructUnitUnknown: z.boolean().default(false),
  originalSuperviseUnit: z.string().optional(),
  originalSuperviseUnitUnknown: z.boolean().default(false),
  
  // ... 其他字段
});
```

**表单处理**:
```typescript
const form = useForm<BuildingProfileFormValues>({
  resolver: zodResolver(buildingProfileSchema),
  defaultValues: {
    clientName: '',
    clientUnit: '',
    // ... 所有字段默认值
  },
});

// 表单变化时通知父组件
useEffect(() => {
  const subscription = form.watch((value) => {
    onChange(value as BuildingProfile);
  });
  return () => subscription.unsubscribe();
}, [form, onChange]);
```

**AI辅助生成**:
```typescript
const handleAIGenerate = async (field: string) => {
  const result = await callGenerateReportData({
    buildingProfile: form.getValues(),
    field: field,
  });
  form.setValue(field, result.content);
};
```

---

### 3.4 损坏构件列表 (DamageComponentList)

**文件路径**: `/client/src/pages/DataCollection/DamageComponentList.tsx`

**功能描述**:
- 展示当前鉴定下的所有损坏构件
- 按构件分类分组展示
- 支持新增、编辑、删除构件
- 支持对单个构件进行AI推理
- 展示构件照片缩略图

**数据结构**:
```typescript
interface ComponentCheck {
  id: string;
  surveyId: string;
  name: string;           // 构件名称（如"混凝土柱"）
  category: string;       // 构件分类（如"上部承重结构"）
  axisLine: string;       // 轴线位置（如"A-1~A-2"）
  checkedItemIds: string[]; // 勾选的评定标准ID列表
  aiEvaluationResult?: string; // AI推理结果
  aiEvaluationClause?: string; // AI推理依据条款
  photos: string[];       // 照片URL列表
  createdAt: string;
}
```

**状态管理**:
```typescript
const [checks, setChecks] = useState<ComponentCheck[]>([]);
const [dialogOpen, setDialogOpen] = useState(false);
const [editingCheck, setEditingCheck] = useState<ComponentCheck | null>(null);
const [aiLoading, setAiLoading] = useState<string | null>(null); // 当前AI推理的构件ID
```

**核心方法**:
```typescript
// 加载构件列表
const loadChecks = async () => {
  const data = await componentCheckApi.getComponentCheckList(surveyId);
  setChecks(data.items);
};

// 打开新增弹窗
const handleAdd = () => {
  setEditingCheck(null);
  setDialogOpen(true);
};

// 打开编辑弹窗
const handleEdit = (check: ComponentCheck) => {
  setEditingCheck(check);
  setDialogOpen(true);
};

// 删除构件
const handleDelete = async (id: string) => {
  await componentCheckApi.deleteComponentCheck(surveyId, id);
  await loadChecks();
};

// 单个构件AI推理
const handleAIReasoning = async (check: ComponentCheck) => {
  setAiLoading(check.id);
  const result = await callHousingSafetyAI({
    singleComponent: check,
  });
  await componentCheckApi.updateComponentCheck(surveyId, check.id, {
    aiEvaluationResult: result.conclusion,
    aiEvaluationClause: result.evaluationClause,
  });
  await loadChecks();
  setAiLoading(null);
};
```

---

### 3.5 损坏构件编辑弹窗 (DamageComponentDialog)

**文件路径**: `/client/src/pages/DataCollection/DamageComponentDialog.tsx`

**功能描述**:
- 新增/编辑损坏构件
- 选择构件分类和类型
- 输入轴线位置
- 勾选评定标准条目（从评定标准库加载）
- 上传构件照片

**表单结构**:
```typescript
interface ComponentCheckFormValues {
  category: string;       // 构件分类（地基基础/上部承重结构/围护结构/其他）
  name: string;           // 构件类型（如混凝土柱）
  axisLine: string;       // 轴线位置
  checkedItemIds: string[]; // 勾选的评定标准ID
  photos: string[];       // 照片URL列表
}
```

**评定标准选择逻辑**:
```typescript
// 1. 选择构件分类后，加载该分类下的构件模板
const componentTemplates = await getComponentTemplates(category);

// 2. 选择构件类型后，加载对应的评定标准
const evaluationStandards = await getEvaluationStandards({
  category,
  componentType: name,
});

// 3. 展示为可勾选的列表
<CheckboxGroup
  options={evaluationStandards.map(s => ({
    label: s.description,
    value: s.id,
  }))}
  value={checkedItemIds}
  onChange={setCheckedItemIds}
/>
```

**照片上传**:
```typescript
const handleUpload = async (files: File[]) => {
  const bucketId = await getDefaultBucketId();
  const uploadedUrls = [];
  for (const file of files) {
    const result = await uploadFile(bucketId, file);
    uploadedUrls.push(result.download_url);
  }
  setPhotos([...photos, ...uploadedUrls]);
};
```

---

### 3.6 报告预览页 (ReportPreview)

**文件路径**: `/client/src/pages/ReportPreview/ReportPreview.tsx`

**功能描述**:
- 展示完整的房屋安全鉴定报告
- 支持导出Word文档
- 支持导出PDF文档
- 打印预览

**报告内容结构**:
```typescript
interface ReportFullData {
  // 基本信息
  surveyNo: string;
  surveyCategory: string;
  clientName: string;
  contactPerson: string;
  contactPhone: string;
  address: string;
  
  // 房屋概况
  buildingProfile: BuildingProfile;
  
  // 损坏构件汇总
  componentChecks: ComponentCheck[];
  
  // 鉴定结论
  conclusion: string;
  basicEvaluation: string;
  
  // 签章信息
  signatures: ReportSignature[];
  
  // 检测图片
  testImages: TestImage[];
}
```

**Word导出实现**:
```typescript
// /client/src/api/report.ts
export async function exportReportWord(id: string): Promise<void> {
  // 1. 获取报告完整数据
  const data = await getReportFullData(id);
  
  // 2. 生成Word文档
  const blob = await generateReportDocx(data);
  
  // 3. 触发下载
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `鉴定报告_${data.surveyNo}.docx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

// Word生成实现
async function generateReportDocx(data: ReportFullData): Promise<Blob> {
  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        // 标题
        new Paragraph({
          text: '房屋安全鉴定书',
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
        }),
        // 编号
        new Paragraph({
          text: `编号：${data.surveyNo}`,
          alignment: AlignmentType.RIGHT,
        }),
        // 一、委托单位
        new Paragraph({
          text: '一、委托单位',
          heading: HeadingLevel.HEADING_1,
        }),
        new Paragraph({
          text: `委托单位：${data.clientName}`,
        }),
        // ... 其他内容
      ],
    }],
  });
  
  return await Packer.toBlob(doc);
}
```

---

### 3.7 AI助手交互页 (AIAssistant)

**文件路径**: `/client/src/pages/AIAssistant/AIAssistant.tsx`

**功能描述**:
- 展示当前鉴定报告内容
- 用户可以输入问题或修改意见
- AI流式输出修改建议和专业批注
- 历史对话记录

**状态管理**:
```typescript
const [survey, setSurvey] = useState<Survey | null>(null);
const [reportContent, setReportContent] = useState('');
const [userQuestion, setUserQuestion] = useState('');
const [aiResponse, setAiResponse] = useState('');
const [isStreaming, setIsStreaming] = useState(false);
const [history, setHistory] = useState<ChatMessage[]>([]);
```

**流式调用实现**:
```typescript
const handleSend = async () => {
  if (!userQuestion.trim()) return;
  
  setIsStreaming(true);
  setAiResponse('');
  
  // 添加到历史记录
  setHistory(prev => [...prev, { role: 'user', content: userQuestion }]);
  
  // 流式调用AI
  await callReportAIAssistant(
    {
      reportContent: reportContent,
      userQuestion: userQuestion,
    },
    (chunk) => {
      // 增量更新响应
      setAiResponse(prev => prev + chunk);
    }
  );
  
  setIsStreaming(false);
  setUserQuestion('');
};
```

---

## 4. API层详细定义

### 4.1 鉴定记录API (survey.ts)

```typescript
// /client/src/api/survey.ts

import { axiosForBackend } from '@lark-apaas/client-toolkit/utils/getAxiosForBackend';

export interface SurveyListParams {
  page?: number;
  pageSize?: number;
  keyword?: string;
}

export interface SurveyListResponse {
  items: Survey[];
  total: number;
}

// 获取鉴定列表
export async function getSurveyList(params: SurveyListParams = {}): Promise<SurveyListResponse> {
  const { page = 1, pageSize = 10, keyword } = params;
  const queryParams = new URLSearchParams();
  queryParams.append('page', String(page));
  queryParams.append('pageSize', String(pageSize));
  if (keyword) queryParams.append('keyword', keyword);
  
  const response = await axiosForBackend({
    url: `/api/surveys?${queryParams.toString()}`,
    method: 'GET',
  });
  return response.data;
}

// 获取鉴定详情
export async function getSurveyById(id: string): Promise<Survey> {
  const response = await axiosForBackend({
    url: `/api/surveys/${id}`,
    method: 'GET',
  });
  return response.data;
}

// 创建鉴定
export async function createSurvey(data: CreateSurveyRequest): Promise<Survey> {
  const response = await axiosForBackend({
    url: '/api/surveys',
    method: 'POST',
    data,
  });
  return response.data;
}

// 更新鉴定
export async function updateSurvey(id: string, data: UpdateSurveyRequest): Promise<Survey> {
  const response = await axiosForBackend({
    url: `/api/surveys/${id}`,
    method: 'PUT',
    data,
  });
  return response.data;
}

// 删除鉴定
export async function deleteSurvey(id: string): Promise<void> {
  await axiosForBackend({
    url: `/api/surveys/${id}`,
    method: 'DELETE',
  });
}

// 获取鉴定标准知识库
export async function getEvaluationStandards(): Promise<EvaluationStandardKnowledgeListResponse> {
  const response = await axiosForBackend({
    url: '/api/surveys/evaluation-standards',
    method: 'GET',
  });
  return response.data;
}
```

### 4.2 损坏构件API (damage-component.ts)

```typescript
// /client/src/api/damage-component.ts

export interface ComponentCheckListResponse {
  items: ComponentCheck[];
}

export interface EvaluationStandardListResponse {
  items: EvaluationStandard[];
}

// 获取构件检查列表
export async function getComponentCheckList(surveyId: string): Promise<ComponentCheckListResponse> {
  const response = await axiosForBackend({
    url: `/api/surveys/${surveyId}/component-checks`,
    method: 'GET',
  });
  return response.data;
}

// 创建构件检查
export async function createComponentCheck(
  surveyId: string, 
  data: CreateComponentCheckRequest
): Promise<ComponentCheck> {
  const response = await axiosForBackend({
    url: `/api/surveys/${surveyId}/component-checks`,
    method: 'POST',
    data,
  });
  return response.data;
}

// 更新构件检查
export async function updateComponentCheck(
  surveyId: string,
  checkId: string,
  data: UpdateComponentCheckRequest
): Promise<ComponentCheck> {
  const response = await axiosForBackend({
    url: `/api/surveys/${surveyId}/component-checks/${checkId}`,
    method: 'PUT',
    data,
  });
  return response.data;
}

// 批量更新构件检查
export async function batchUpdateComponentChecks(
  surveyId: string,
  data: BatchUpdateComponentCheckRequest
): Promise<void> {
  await axiosForBackend({
    url: `/api/surveys/${surveyId}/component-checks/batch`,
    method: 'PUT',
    data,
  });
}

// 删除构件检查
export async function deleteComponentCheck(surveyId: string, checkId: string): Promise<void> {
  await axiosForBackend({
    url: `/api/surveys/${surveyId}/component-checks/${checkId}`,
    method: 'DELETE',
  });
}

// 获取评定标准列表
export async function getEvaluationStandards(params?: {
  category?: string;
  componentType?: string;
}): Promise<EvaluationStandardListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.category) queryParams.append('category', params.category);
  if (params?.componentType) queryParams.append('componentType', params.componentType);
  
  const response = await axiosForBackend({
    url: `/api/evaluation-standards${queryParams.toString() ? `?${queryParams.toString()}` : ''}`,
    method: 'GET',
  });
  return response.data;
}

// 获取构件模板列表
export async function getComponentTemplates(): Promise<ComponentTemplateListResponse> {
  const response = await axiosForBackend({
    url: '/api/component-templates',
    method: 'GET',
  });
  return response.data;
}
```

### 4.3 AI插件API (ai-plugin.ts)

```typescript
// /client/src/api/ai-plugin.ts

import { capabilityClient } from '@lark-apaas/client-toolkit';

// 房屋安全鉴定AI推理（非流式）
export interface HousingSafetyAIRequest {
  buildingInfo: {
    address: string;
    buildYear?: string;
    structureType?: string;
    floorCount?: number;
    buildArea?: number;
    floorHeight?: number;
    totalHeight?: number;
  };
  componentChecks: ComponentCheck[];
}

export interface HousingSafetyAIResponse {
  conclusion: string;      // A/B/C/D级
  basicEvaluation: string; // 基础评定
  riskLevel: string;       // 低/中/高风险
  suggestion: string;      // 处理建议
}

export async function callHousingSafetyAI(
  request: HousingSafetyAIRequest
): Promise<HousingSafetyAIResponse> {
  const plugin = capabilityClient.load('housing_safety_assessment_ai_inference_1');
  const result = await plugin.call('generate', {
    building_info: JSON.stringify(request.buildingInfo),
    damage_components: JSON.stringify(request.componentChecks),
  });
  return JSON.parse(result.output);
}

// 鉴定报告AI修改助手（流式）
export interface ReportAIAssistantRequest {
  reportContent: string;
  userQuestion?: string;
}

export async function callReportAIAssistant(
  request: ReportAIAssistantRequest,
  onChunk: (chunk: string) => void
): Promise<void> {
  const plugin = capabilityClient.load('ai_report_modification_assistant_1');
  const stream = await plugin.callStream('generate', {
    report_content: request.reportContent,
    user_question: request.userQuestion || '',
  });
  
  for await (const chunk of stream) {
    onChunk(chunk);
  }
}

// 鉴定报告AI修改助手（非流式）
export async function callReportAIAssistantUnary(
  request: ReportAIAssistantRequest
): Promise<string> {
  const plugin = capabilityClient.load('ai_report_modification_assistant_1');
  const result = await plugin.call('generate', {
    report_content: request.reportContent,
    user_question: request.userQuestion || '',
  });
  return result.output;
}

// AI生成报告数据字段
export interface GenerateReportDataRequest {
  buildingProfile: BuildingProfile;
  field: string; // 要生成的字段名
}

export async function callGenerateReportData(
  request: GenerateReportDataRequest
): Promise<{ content: string }> {
  const plugin = capabilityClient.load('report_data_generation_1');
  const result = await plugin.call('generate', {
    building_profile: JSON.stringify(request.buildingProfile),
    field: request.field,
  });
  return { content: result.output };
}
```

### 4.4 报告API (report.ts)

```typescript
// /client/src/api/report.ts

import { Document, Packer, Paragraph, HeadingLevel, AlignmentType } from 'docx';
import { saveAs } from 'file-saver';

// 获取报告内容
export async function getReport(id: string): Promise<Report> {
  const response = await axiosForBackend({
    url: `/api/reports/${id}`,
    method: 'GET',
  });
  return response.data;
}

// 获取报告完整数据
export async function getReportFullData(id: string): Promise<ReportFullData> {
  const response = await axiosForBackend({
    url: `/api/reports/${id}/full-data`,
    method: 'GET',
  });
  return response.data;
}

// 生成并下载Word报告
export async function generateReportDocx(data: ReportFullData): Promise<Blob> {
  const doc = new Document({
    sections: [{
      properties: {},
      children: [
        new Paragraph({
          text: '房屋安全鉴定书',
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({ text: `编号：${data.surveyNo}` }),
        new Paragraph({ text: '' }),
        new Paragraph({
          text: '一、委托单位',
          heading: HeadingLevel.HEADING_1,
        }),
        new Paragraph({ text: `委托单位：${data.clientName || ''}` }),
        new Paragraph({ text: `联系人：${data.contactPerson || ''}` }),
        new Paragraph({ text: `联系电话：${data.contactPhone || ''}` }),
        new Paragraph({ text: '' }),
        new Paragraph({
          text: '二、房屋概况',
          heading: HeadingLevel.HEADING_1,
        }),
        new Paragraph({ text: `房屋地址：${data.address}` }),
        new Paragraph({ text: `结构类型：${data.buildingProfile?.structureInfo?.structureType?.join('、') || ''}` }),
        new Paragraph({ text: `建筑面积：${data.buildArea || ''}㎡` }),
        new Paragraph({ text: `建造年代：${data.buildYear || ''}` }),
        new Paragraph({ text: '' }),
        new Paragraph({
          text: '三、损坏构件查勘',
          heading: HeadingLevel.HEADING_1,
        }),
        // ... 构件列表
        new Paragraph({ text: '' }),
        new Paragraph({
          text: '四、鉴定结论',
          heading: HeadingLevel.HEADING_1,
        }),
        new Paragraph({ text: `安全等级：${data.conclusion || ''}` }),
        new Paragraph({ text: data.basicEvaluation || '' }),
      ],
    }],
  });
  
  return await Packer.toBlob(doc);
}

// 导出Word报告
export async function exportReportWord(id: string, fileName?: string): Promise<void> {
  const data = await getReportFullData(id);
  const blob = await generateReportDocx(data);
  saveAs(blob, fileName || `鉴定报告_${data.surveyNo || id}.docx`);
}
```

---

## 5. 共享类型定义 (shared/api.interface.ts)

```typescript
// /shared/api.interface.ts

// ==================== Survey 相关 ====================

export interface AIReasoningResult {
  conclusion: string;
  basicEvaluation: string;
  riskLevel: string;
  suggestion: string;
}

export interface Survey {
  id: string;
  address: string;
  buildYear: string;
  structureType: string;
  floorCount: number;
  buildArea: number;
  surveyTime: string;
  conclusion: string;
  basicEvaluation: string;
  aiReasoningResult: AIReasoningResult | null;
  status: 'draft' | 'completed' | 'exported';
  createdAt: string;
  buildingProfile?: BuildingProfile;
  reportData?: ReportData;
  surveyNo?: string;
  surveyCategory?: string;
  surveyCategoryDesc?: string;
  surveyPurpose?: string;
  clientName?: string;
  contactPerson?: string;
  contactPhone?: string;
  houseName?: string;
  propertyNature?: string;
  propertyCertificateNo?: string;
  eavesHeight?: string;
  currentUsage?: string;
  usageHistory?: string;
  externalEnvironment?: string;
}

export interface CreateSurveyRequest {
  address?: string;
}

export interface UpdateSurveyRequest {
  address?: string;
  buildYear?: string;
  structureType?: string;
  floorCount?: number;
  buildArea?: number;
  surveyTime?: string;
  conclusion?: string;
  basicEvaluation?: string;
  aiReasoningResult?: AIReasoningResult;
  status?: 'draft' | 'completed' | 'exported';
  buildingProfile?: BuildingProfile;
  reportData?: ReportData;
  surveyNo?: string;
  surveyCategory?: string;
  surveyCategoryDesc?: string;
  surveyPurpose?: string;
  clientName?: string;
  contactPerson?: string;
  contactPhone?: string;
}

export interface SurveyListResponse {
  items: Survey[];
  total: number;
}

// ==================== BuildingProfile 房屋概况 ====================

export interface BuildingProfile {
  basicInfo: BuildingBasicInfo;
  clientInfo: ClientInfo;
  purposeInfo: PurposeInfo;
  structureInfo: StructureInfo;
  historyChange: HistoryChange;
  usageStatus: UsageStatus;
  selfBuiltInfo: SelfBuiltInfo;
  textDescription: TextDescription;
}

export interface BuildingBasicInfo {
  buildingName: string;
  surveyType: string;
  location: string;
  propertyRight: string;
  buildArea: number;
  totalHeight: number;
  certificateNo: string;
  buildYear: string;
  floorHeight: number;
  floorCount: number;
  originalSurveyUnit: string;
  originalDesignUnit: string;
  originalConstructUnit: string;
  originalSuperviseUnit: string;
  originalSurveyUnitUnknown: boolean;
  originalDesignUnitUnknown: boolean;
  originalConstructUnitUnknown: boolean;
  originalSuperviseUnitUnknown: boolean;
  propertyNature: string;
  propertyCertificateNo: string;
  eavesHeight: string;
}

export interface ClientInfo {
  clientName: string;
  clientUnit: string;
  contactPerson: string;
  contactPhone: string;
}

export interface PurposeInfo {
  originalPurpose: string[];
  currentPurpose: string[];
  originalPurposeOther: string;
  currentPurposeOther: string;
}

export interface StructureInfo {
  structureType: string[];
  foundationType: string[];
  foundationTreatment: string[];
  wallType: string[];
  floorType: string[];
  roofStructure: string[];
  stairType: string[];
  seismicLevel: string;
  seismicUnknown: boolean;
  seismicNone: boolean;
  structureTypeOther: string;
  foundationTypeOther: string;
  foundationTreatmentOther: string;
  wallTypeOther: string;
  floorTypeOther: string;
  roofStructureOther: string;
  stairTypeOther: string;
}

export interface HistoryChange {
  purposeChange: 'has' | 'none' | 'unknown';
  renovation: 'has' | 'none' | 'unknown';
  reinforcement: 'has' | 'none' | 'unknown';
  disaster: 'has' | 'none' | 'unknown';
}

export interface UsageStatus {
  structureModification: 'has' | 'none' | 'unknown';
  illegalConstruction: 'has' | 'none' | 'unknown';
  overloadUsage: 'has' | 'none' | 'unknown';
  other: 'has' | 'none' | 'unknown';
}

export interface SelfBuiltInfo {
  isCulturalRelic: boolean;
  isRuralRenovation: boolean;
  isTrainingInstitution: boolean;
  isSelfBuiltReport: boolean;
  isSelfBuilt: boolean;
  isCommercialSelfBuilt: boolean;
  isRuralDangerousRepair: boolean;
  isProtectedBuilding: boolean;
  isHistoricalCertificate: boolean;
  selfBuiltCheckCode: string;
  censusHouseNo: string;
}

export interface TextDescription {
  usageHistory: string;
  externalEnvironment: string;
  structureCondition: string;
  remarks: string;
  clientMaterials: string[];
  clientMaterialsOther: string;
  surroundingEnvironment: string;
  surroundingEnvironmentDesc: string;
}

// ==================== ComponentCheck 损坏构件 ====================

export interface ComponentCheck {
  id: string;
  surveyId: string;
  name: string;
  category: string;
  axisLine: string;
  checkedItemIds: string[];
  aiEvaluationResult: string;
  aiEvaluationClause: string;
  photos: string[];
  createdAt: string;
}

export interface CreateComponentCheckRequest {
  name: string;
  category: string;
  axisLine?: string;
  checkedItemIds: string[];
  photos?: string[];
}

export interface UpdateComponentCheckRequest {
  name?: string;
  category?: string;
  axisLine?: string;
  checkedItemIds?: string[];
  aiEvaluationResult?: string;
  aiEvaluationClause?: string;
  photos?: string[];
}

export interface BatchUpdateComponentCheckRequest {
  items: Array<{
    id: string;
    aiEvaluationResult?: string;
    aiEvaluationClause?: string;
  }>;
}

export interface ComponentCheckListResponse {
  items: ComponentCheck[];
}

// ==================== EvaluationStandard 评定标准 ====================

export interface EvaluationStandard {
  id: string;
  category: string;
  componentType: string;
  description: string;
  evaluationResult?: string;
  evaluationClause?: string;
  sortOrder: number;
}

export interface EvaluationStandardListResponse {
  items: EvaluationStandard[];
}

// ==================== ComponentTemplate 构件模板 ====================

export interface ComponentTemplate {
  id: string;
  category: string;
  name: string;
  checkItems: Array<{
    name: string;
    type: 'checkbox' | 'input';
    options?: string[];
  }>;
  displayOrder: number;
}

export interface ComponentTemplateListResponse {
  items: ComponentTemplate[];
}

// ==================== ReportData 报告数据 ====================

export interface ReportData {
  clientProvidedMaterials?: string;
  evaluationStandards?: string[];
  usageHistory?: string;
  externalEnvironment?: string;
  structureCondition?: string;
  remarks?: string;
}

// ==================== Report 报告 ====================

export interface Report {
  id: string;
  surveyId: string;
  content: string;
  status: string;
  createdAt: string;
}

export interface ReportFullData extends Survey {
  componentChecks: ComponentCheck[];
  signatures: ReportSignature[];
  testImages: TestImage[];
}

// ==================== ReportSignature 报告签章 ====================

export interface ReportSignature {
  id: string;
  surveyId: string;
  type: string;
  signatoryName: string;
  imageUrl: string;
  signDate: string;
}

// ==================== TestImage 检测图片 ====================

export interface TestImage {
  id: string;
  surveyId: string;
  type: string;
  label: string;
  imageUrl: string;
  sortOrder: number;
}

// ==================== StructuralTestResult 结构检测结果 ====================

export interface StructuralTestResult {
  id: string;
  surveyId: string;
  testUnit: string;
  certificateNo: string;
  testPersonnel: string;
  reportNo: string;
  testDate: string;
  mainTestContent: string;
  testStandards: string;
  testResultsSummary: string;
}

// ==================== EvaluationStandardKnowledge 鉴定标准知识库 ====================

export interface EvaluationStandardKnowledge {
  id: string;
  name: string;
  code: string;
  type: string;
  content: string;
  isDefault: boolean;
}

export interface EvaluationStandardKnowledgeListResponse {
  items: EvaluationStandardKnowledge[];
}

export interface CreateEvaluationStandardKnowledgeRequest {
  name: string;
  code: string;
  type: string;
  content: string;
  isDefault?: boolean;
}

export interface UpdateEvaluationStandardKnowledgeRequest {
  name?: string;
  code?: string;
  type?: string;
  content?: string;
  isDefault?: boolean;
}
```

---

## 6. 后端模块详细规格

### 6.1 SurveyModule (鉴定记录模块)

**文件路径**:
- `/server/modules/survey/survey.module.ts`
- `/server/modules/survey/survey.controller.ts`
- `/server/modules/survey/survey.service.ts`

**Controller API**:
```typescript
@Controller('api/surveys')
export class SurveyController {
  @Get()
  async getSurveys(@Query() query: GetSurveyListDto): Promise<SurveyListResponse>;

  @Post()
  async createSurvey(@Body() dto: CreateSurveyDto): Promise<Survey>;

  @Get(':id')
  async getSurveyById(@Param('id') id: string): Promise<Survey>;

  @Put(':id')
  async updateSurvey(@Param('id') id: string, @Body() dto: UpdateSurveyDto): Promise<Survey>;

  @Delete(':id')
  async deleteSurvey(@Param('id') id: string): Promise<void>;

  @Get('evaluation-standards')
  async getEvaluationStandards(): Promise<EvaluationStandardKnowledgeListResponse>;
}
```

### 6.2 DamageComponentModule (损坏构件模块)

**文件路径**:
- `/server/modules/damage-component/damage-component.module.ts`
- `/server/modules/damage-component/damage-component.controller.ts`
- `/server/modules/damage-component/damage-component.service.ts`
- `/server/modules/damage-component/evaluation-standard.controller.ts`
- `/server/modules/damage-component/component-template.controller.ts`

**Controller API**:
```typescript
// damage-component.controller.ts
@Controller('api/surveys/:surveyId/component-checks')
export class DamageComponentController {
  @Get()
  async getComponentChecks(@Param('surveyId') surveyId: string): Promise<ComponentCheckListResponse>;

  @Post()
  async createComponentCheck(
    @Param('surveyId') surveyId: string,
    @Body() dto: CreateComponentCheckDto
  ): Promise<ComponentCheck>;

  @Put(':id')
  async updateComponentCheck(
    @Param('surveyId') surveyId: string,
    @Param('id') id: string,
    @Body() dto: UpdateComponentCheckDto
  ): Promise<ComponentCheck>;

  @Put('batch')
  async batchUpdateComponentChecks(
    @Param('surveyId') surveyId: string,
    @Body() dto: BatchUpdateComponentCheckDto
  ): Promise<void>;

  @Delete(':id')
  async deleteComponentCheck(
    @Param('surveyId') surveyId: string,
    @Param('id') id: string
  ): Promise<void>;
}

// evaluation-standard.controller.ts
@Controller('api/evaluation-standards')
export class EvaluationStandardController {
  @Get()
  async getEvaluationStandards(
    @Query('category') category?: string,
    @Query('componentType') componentType?: string
  ): Promise<EvaluationStandardListResponse>;
}

// component-template.controller.ts
@Controller('api/component-templates')
export class ComponentTemplateController {
  @Get()
  async getComponentTemplates(): Promise<ComponentTemplateListResponse>;
}
```

### 6.3 ReportModule (报告模块)

**文件路径**:
- `/server/modules/report/report.module.ts`
- `/server/modules/report/report.controller.ts`
- `/server/modules/report/report.service.ts`
- `/server/modules/report/report-generators.ts`

**Controller API**:
```typescript
@Controller('api/reports')
export class ReportController {
  @Get(':id')
  async getReport(@Param('id') id: string): Promise<Report>;

  @Get(':id/full-data')
  async getReportFullData(@Param('id') id: string): Promise<ReportFullData>;

  @Get(':id/export')
  async exportReportWord(@Param('id') id: string, @Res() res: Response): Promise<void>;
}
```

---

## 7. 数据库Schema定义

### 7.1 表结构

```typescript
// /server/database/schema.ts

// 鉴定记录表
export const survey = pgTable("survey", {
  id: uuid().defaultRandom().notNull(),
  address: varchar({ length: 255 }).notNull(),
  buildYear: varchar("build_year", { length: 50 }),
  structureType: varchar("structure_type", { length: 100 }),
  floorCount: integer("floor_count"),
  buildArea: numeric("build_area", { precision: 10, scale: 2 }),
  surveyTime: customTimestamptz('survey_time'),
  conclusion: text(),
  basicEvaluation: text("basic_evaluation"),
  aiReasoningResult: jsonb("ai_reasoning_result"),
  status: varchar({ length: 50 }).default('draft'),
  creator: userProfile("creator"),
  buildingProfile: jsonb("building_profile"),
  reportData: jsonb("report_data"),
  surveyNo: varchar("survey_no", { length: 100 }),
  surveyCategory: varchar("survey_category", { length: 100 }),
  clientName: varchar("client_name", { length: 255 }),
  contactPerson: varchar("contact_person", { length: 100 }),
  contactPhone: varchar("contact_phone", { length: 50 }),
  houseName: varchar("house_name", { length: 255 }),
  propertyNature: varchar("property_nature", { length: 100 }),
  propertyCertificateNo: varchar("property_certificate_no", { length: 255 }),
  eavesHeight: varchar("eaves_height", { length: 50 }),
  currentUsage: varchar("current_usage", { length: 100 }),
  usageHistory: text("usage_history"),
  externalEnvironment: text("external_environment"),
  evaluationStandards: text("evaluation_standards"),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});

// 构件检查记录表
export const componentCheck = pgTable("component_check", {
  id: uuid().defaultRandom().notNull(),
  surveyId: uuid("survey_id").notNull(),
  name: varchar({ length: 100 }),
  category: varchar({ length: 100 }),
  axisLine: varchar("axis_line", { length: 100 }),
  checkedItemIds: jsonb("checked_item_ids").default([]),
  aiEvaluationResult: varchar("ai_evaluation_result", { length: 255 }),
  aiEvaluationClause: varchar("ai_evaluation_clause", { length: 255 }),
  photos: text().array(),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});

// 评定标准表
export const evaluationStandard = pgTable("evaluation_standard", {
  id: uuid().defaultRandom().notNull(),
  category: varchar({ length: 100 }).notNull(),
  componentType: varchar("component_type", { length: 100 }).notNull(),
  description: text().notNull(),
  evaluationResult: varchar("evaluation_result", { length: 255 }),
  evaluationClause: varchar("evaluation_clause", { length: 255 }),
  sortOrder: integer("sort_order").default(0),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});

// 构件模板表
export const componentTemplate = pgTable("component_template", {
  id: uuid().defaultRandom().notNull(),
  category: varchar({ length: 100 }).notNull(),
  name: varchar({ length: 100 }).notNull(),
  checkItems: jsonb("check_items").notNull(),
  displayOrder: integer("display_order").default(0),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});

// 鉴定标准知识库表
export const evaluationStandardKnowledge = pgTable("evaluation_standard_knowledge", {
  id: uuid().defaultRandom().notNull(),
  name: varchar({ length: 255 }).notNull(),
  code: varchar({ length: 255 }).notNull(),
  type: varchar({ length: 50 }).notNull(),
  content: text(),
  isDefault: boolean("is_default").default(false),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});

// 结构检测结果表
export const structuralTestResult = pgTable("structural_test_result", {
  id: uuid().defaultRandom().notNull(),
  surveyId: uuid("survey_id").notNull(),
  testUnit: varchar("test_unit", { length: 255 }),
  certificateNo: varchar("certificate_no", { length: 255 }),
  testPersonnel: varchar("test_personnel", { length: 255 }),
  reportNo: varchar("report_no", { length: 255 }),
  testDate: customTimestamptz('test_date'),
  mainTestContent: text("main_test_content"),
  testStandards: text("test_standards"),
  testResultsSummary: text("test_results_summary"),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});

// 报告签章表
export const reportSignature = pgTable("report_signature", {
  id: uuid().defaultRandom().notNull(),
  surveyId: uuid("survey_id").notNull(),
  type: varchar({ length: 50 }).notNull(),
  signatoryName: varchar("signatory_name", { length: 255 }),
  imageUrl: text("image_url"),
  signDate: customTimestamptz('sign_date'),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});

// 检测图片表
export const testImage = pgTable("test_image", {
  id: uuid().defaultRandom().notNull(),
  surveyId: uuid("survey_id").notNull(),
  type: varchar({ length: 50 }).notNull(),
  label: varchar({ length: 255 }),
  imageUrl: text("image_url").notNull(),
  sortOrder: integer("sort_order").default(0),
  createdAt: customTimestamptz('_created_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  createdBy: userProfile("_created_by"),
  updatedAt: customTimestamptz('_updated_at').default(sql`CURRENT_TIMESTAMP`).notNull(),
  updatedBy: userProfile("_updated_by"),
});
```

---

## 8. 插件配置详情

### 8.1 房屋安全鉴定AI推理插件

**文件路径**: `/server/capabilities/housing_safety_assessment_ai_inference_1.json`

```json
{
  "id": "housing_safety_assessment_ai_inference_1",
  "plugin": "@official-plugins/ai-text-to-json",
  "name": "房屋安全鉴定AI推理",
  "description": "根据房屋信息和损坏构件自动推理鉴定结论",
  "outputMode": "unary",
  "inputSchema": {
    "type": "object",
    "properties": {
      "building_info": {
        "type": "string",
        "description": "JSON字符串格式的房屋基础信息"
      },
      "damage_components": {
        "type": "string",
        "description": "JSON字符串格式的损坏构件数组"
      }
    },
    "required": ["building_info"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "conclusion": {
        "type": "string",
        "description": "鉴定结论：A/B/C/D级"
      },
      "basicEvaluation": {
        "type": "string",
        "description": "基础评定详细描述"
      },
      "riskLevel": {
        "type": "string",
        "description": "风险等级：低/中/高"
      },
      "suggestion": {
        "type": "string",
        "description": "处理建议"
      }
    }
  }
}
```

### 8.2 鉴定报告AI修改助手插件

**文件路径**: `/server/capabilities/ai_report_modification_assistant_1.json`

```json
{
  "id": "ai_report_modification_assistant_1",
  "plugin": "@official-plugins/ai-text-generate",
  "name": "鉴定报告AI修改助手",
  "description": "针对鉴定报告内容提供专业修改意见和建议",
  "outputMode": "stream",
  "inputSchema": {
    "type": "object",
    "properties": {
      "report_content": {
        "type": "string",
        "description": "鉴定报告完整内容"
      },
      "user_question": {
        "type": "string",
        "description": "用户的具体问题或修改意见"
      }
    },
    "required": ["report_content"]
  },
  "outputSchema": {
    "type": "string",
    "description": "AI修改建议和专业批注（流式输出）"
  }
}
```

---

## 9. 路由配置

```typescript
// /client/src/app.tsx

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import SurveyList from './pages/SurveyList/SurveyList';
import DataCollection from './pages/DataCollection/DataCollection';
import ReportPreview from './pages/ReportPreview/ReportPreview';
import OriginalRecordPreview from './pages/OriginalRecordPreview/OriginalRecordPreview';
import AIAssistant from './pages/AIAssistant/AIAssistant';
import NotFound from './pages/NotFound/NotFound';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<SurveyList />} />
          <Route path="survey/:id" element={<DataCollection />} />
          <Route path="report/:id" element={<ReportPreview />} />
          <Route path="original-record/:id" element={<OriginalRecordPreview />} />
          <Route path="ai-assistant/:id" element={<AIAssistant />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 10. 开发环境配置

### 10.1 依赖列表

**核心依赖**:
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^6.x",
    "@tanstack/react-query": "^5.x",
    "react-hook-form": "^7.x",
    "@hookform/resolvers": "^3.x",
    "zod": "^3.x",
    "docx": "^8.x",
    "file-saver": "^2.x",
    "@lark-apaas/client-toolkit": "latest",
    "@lark-apaas/fullstack-nestjs-core": "latest"
  }
}
```

### 10.2 环境变量

```env
# 开发环境
NODE_ENV=development

# 生产环境
NODE_ENV=production
```

---

## 11. 关键实现细节

### 11.1 表单联动逻辑

**原参建单位"不详"勾选联动**:
```typescript
// 当勾选"不详"时，清空对应输入框并禁用
<FormField
  control={form.control}
  name="originalSurveyUnitUnknown"
  render={({ field }) => (
    <FormItem className="flex items-center space-x-2">
      <FormControl>
        <Checkbox
          checked={field.value}
          onCheckedChange={(checked) => {
            field.onChange(checked);
            if (checked) {
              form.setValue('originalSurveyUnit', '');
            }
          }}
        />
      </FormControl>
      <FormLabel className="!mt-0">不详</FormLabel>
    </FormItem>
  )}
/>
<Input
  {...form.register('originalSurveyUnit')}
  disabled={form.watch('originalSurveyUnitUnknown')}
/>
```

### 11.2 AI推理状态管理

```typescript
// 全局AI推理状态
const [aiLoading, setAiLoading] = useState(false);
const [aiProgress, setAiProgress] = useState('');

// 执行AI推理
const handleAIReasoning = async () => {
  setAiLoading(true);
  setAiProgress('正在分析房屋信息...');
  
  try {
    const result = await callHousingSafetyAI({
      buildingInfo: extractBuildingInfo(buildingProfile),
      componentChecks: componentChecks,
    });
    
    setAiProgress('推理完成，正在保存结果...');
    await updateSurvey(id, {
      conclusion: result.conclusion,
      basicEvaluation: result.basicEvaluation,
      aiReasoningResult: result,
    });
    
    toast.success('AI推理完成');
  } catch (error) {
    toast.error('AI推理失败');
  } finally {
    setAiLoading(false);
    setAiProgress('');
  }
};
```

### 11.3 自动保存草稿

```typescript
// 使用debounce实现自动保存
const debouncedSave = useMemo(
  () => debounce(async (data: BuildingProfile) => {
    await updateSurvey(id, { buildingProfile: data });
    setLastSavedAt(new Date());
  }, 2000),
  [id]
);

// 监听表单变化
useEffect(() => {
  const subscription = form.watch((value) => {
    debouncedSave(value as BuildingProfile);
  });
  return () => subscription.unsubscribe();
}, [form, debouncedSave]);
```

---

## 12. 常见问题与解决方案

### 12.1 表单性能优化

**问题**: 房屋概况表单字段过多（200+），频繁重渲染导致卡顿。

**解决方案**:
1. 使用 `useForm` 的 `mode: 'onBlur'` 减少验证频率
2. 复杂字段分组使用独立子组件
3. 使用 `React.memo` 优化子组件
4. 使用 `useWatch` 替代 `watch` 监听特定字段

### 12.2 图片上传处理

**问题**: 多张照片同时上传时内存占用高。

**解决方案**:
1. 串行上传而非并行
2. 上传前压缩图片
3. 使用缩略图展示，点击后查看大图

### 12.3 AI推理超时

**问题**: AI推理耗时较长，用户等待体验差。

**解决方案**:
1. 添加进度提示
2. 支持后台推理，完成后通知
3. 添加取消按钮

---

## 附录：构件分类体系

### 一级分类
1. **地基基础** - 地基、基础
2. **上部承重结构** - 混凝土柱、砖柱、砖墙、混凝土梁、混凝土板、屋架
3. **围护结构** - 砌体自承重墙、填充墙、门窗洞口过梁、挑梁、雨棚板、女儿墙
4. **其他** - 楼地面、屋面、非承重墙、门窗、抹灰、顶棚等

### 二级分类（构件类型）示例
| 一级分类 | 二级分类 |
|---------|---------|
| 上部承重结构 | 混凝土柱、砖柱、砖墙、混凝土梁、混凝土板、屋架 |
| 围护结构 | 砌体自承重墙、填充墙、门窗洞口过梁、挑梁、雨棚板、女儿墙 |
| 地基基础 | 地基、基础 |
