import request from './request.js'

// 获取结构检测结果列表
export function getStructuralTestResults(surveyId) {
  return request.get(`/surveys/${surveyId}/structural-test-results`)
}

// 创建结构检测结果
export function createStructuralTestResult(data) {
  return request.post(`/surveys/${data.survey_id}/structural-test-results`, data)
}

// 更新结构检测结果
export function updateStructuralTestResult(surveyId, id, data) {
  return request.put(`/surveys/${surveyId}/structural-test-results/${id}`, data)
}

// 删除结构检测结果
export function deleteStructuralTestResult(surveyId, id) {
  return request.delete(`/surveys/${surveyId}/structural-test-results/${id}`)
}
