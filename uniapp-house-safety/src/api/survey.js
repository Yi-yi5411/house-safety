import request from './request.js'

// ===== Survey CRUD =====

// 获取鉴定列表 (supports page, page_size, status, keyword params)
export function getSurveyList(params = {}) {
  return request.get('/surveys/', params)
}

// 获取鉴定详情
export function getSurveyDetail(id) {
  return request.get(`/surveys/${id}`)
}

// 创建鉴定
export function createSurvey(data) {
  return request.post('/surveys/', data)
}

// 更新鉴定
export function updateSurvey(id, data) {
  return request.put(`/surveys/${id}`, data)
}

// 删除鉴定
export function deleteSurvey(id) {
  return request.delete(`/surveys/${id}`)
}

// ===== Reports =====

// 获取报告完整数据
export function getReportFullData(id) {
  return request.get(`/reports/${id}/full-data`)
}

// 导出报告 (.docx)
export function exportReport(id) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.downloadFile({
      url: `http://127.0.0.1:8000/api/v1/reports/${id}/export`,
      header: { 'Authorization': token ? `Bearer ${token}` : '' },
      success: (res) => resolve(res.tempFilePath),
      fail: reject
    })
  })
}

// ===== Original Records =====

// 获取原始记录数据
export function getOriginalRecord(id) {
  return request.get(`/original-records/${id}`)
}

// 导出原始记录 (.docx)
export function exportOriginalRecord(id) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.downloadFile({
      url: `http://127.0.0.1:8000/api/v1/original-records/${id}/export`,
      header: { 'Authorization': token ? `Bearer ${token}` : '' },
      success: (res) => resolve(res.tempFilePath),
      fail: reject
    })
  })
}

// ===== AI =====

// AI推理
export function aiReasoning(surveyId, prompt) {
  return request.post('/ai/reason', { survey_id: surveyId, prompt })
}

// AI文本生成 (usage_history, external_environment, structure_condition, remarks)
export function aiGenerateText(type, context) {
  return request.post(`/ai/text/${type}`, context)
}
