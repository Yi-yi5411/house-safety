import request from './request.js'

// 获取报告模板列表
export function getReportTemplates() {
  return request.get('/report-templates/')
}

// 获取当前激活的模板
export function getActiveTemplate() {
  return request.get('/report-templates/active')
}

// 创建报告模板
export function createReportTemplate(data) {
  return request.post('/report-templates/', data)
}

// 设置激活模板
export function setActiveTemplate(id) {
  return request.put(`/report-templates/${id}/active`)
}

// 删除报告模板
export function deleteReportTemplate(id) {
  return request.delete(`/report-templates/${id}`)
}
