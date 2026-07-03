import request from './request.js'

// ===== Component Checks =====

// 获取构件检查列表 (filter by survey_id query param)
export function getComponentCheckList(surveyId) {
  return request.get('/components/', { survey_id: surveyId })
}

// 创建构件检查
export function createComponentCheck(data) {
  return request.post('/components/', data)
}

// 更新构件检查
export function updateComponentCheck(id, data) {
  return request.put(`/components/${id}`, data)
}

// 删除构件检查
export function deleteComponentCheck(id) {
  return request.delete(`/components/${id}`)
}

// ===== Evaluation Standards =====

// 获取评定标准列表 (supports category, componentType filters)
export function getEvaluationStandards(params = {}) {
  return request.get('/components/standards', params)
}

// ===== Component Templates =====

// 获取构件模板列表
export function getComponentTemplates() {
  return request.get('/component-templates/')
}
