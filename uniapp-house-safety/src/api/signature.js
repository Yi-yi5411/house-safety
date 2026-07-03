import request from './request.js'

// 获取签字盖章列表
export function getSignatures(surveyId) {
  return request.get(`/surveys/${surveyId}/signatures`)
}

// 创建签字盖章
export function createSignature(surveyId, data) {
  return request.post(`/surveys/${surveyId}/signatures`, data)
}

// 更新签字盖章
export function updateSignature(surveyId, id, data) {
  return request.put(`/surveys/${surveyId}/signatures/${id}`, data)
}

// 删除签字盖章
export function deleteSignature(surveyId, id) {
  return request.delete(`/surveys/${surveyId}/signatures/${id}`)
}
