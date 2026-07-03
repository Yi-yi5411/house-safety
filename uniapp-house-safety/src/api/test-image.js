import request from './request.js'

// 获取检测图片列表
export function getTestImages(surveyId) {
  return request.get(`/surveys/${surveyId}/test-images`)
}

// 创建检测图片
export function createTestImage(surveyId, data) {
  return request.post(`/surveys/${surveyId}/test-images`, data)
}

// 更新检测图片
export function updateTestImage(surveyId, id, data) {
  return request.put(`/surveys/${surveyId}/test-images/${id}`, data)
}

// 删除检测图片
export function deleteTestImage(surveyId, id) {
  return request.delete(`/surveys/${surveyId}/test-images/${id}`)
}

// 重新排序检测图片
export function reorderTestImages(surveyId, items) {
  return request.put(`/surveys/${surveyId}/test-images/reorder`, { items })
}
