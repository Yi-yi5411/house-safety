/**
 * Report and original record API module.
 * Export (docx/pdf), full data, templates, evaluation standard knowledge.
 */
import request from './request'

const BASE_URL = 'http://127.0.0.1:8000/api/v1'

// ==================== Report ====================

/**
 * Get full report data for a survey.
 * GET /api/v1/reports/{surveyId}/full-data
 */
export function getReportFullData(surveyId) {
  return request.get(`/reports/${surveyId}/full-data`)
}

/**
 * Export report as DOCX.
 * GET /api/v1/reports/{surveyId}/export
 * Returns a download URL.
 */
export function exportReportDocx(surveyId) {
  return `${BASE_URL}/reports/${surveyId}/export`
}

/**
 * Export report as PDF.
 * GET /api/v1/reports/{surveyId}/export/pdf
 * Returns a download URL.
 */
export function exportReportPdf(surveyId) {
  return `${BASE_URL}/reports/${surveyId}/export/pdf`
}

// ==================== Original Record ====================

/**
 * Get original record data.
 * GET /api/v1/original-records/{surveyId}
 */
export function getOriginalRecord(surveyId) {
  return request.get(`/original-records/${surveyId}`)
}

/**
 * Export original record as DOCX.
 * GET /api/v1/original-records/{surveyId}/export
 */
export function exportOriginalRecordDocx(surveyId) {
  return `${BASE_URL}/original-records/${surveyId}/export`
}

/**
 * Export original record as PDF.
 * GET /api/v1/original-records/{surveyId}/export/pdf
 */
export function exportOriginalRecordPdf(surveyId) {
  return `${BASE_URL}/original-records/${surveyId}/export/pdf`
}

// ==================== Report Templates ====================

/**
 * List all report templates.
 * GET /api/v1/report-templates/
 */
export function listReportTemplates() {
  return request.get('/report-templates/')
}

/**
 * Get active report template.
 * GET /api/v1/report-templates/active
 */
export function getActiveTemplate() {
  return request.get('/report-templates/active')
}

/**
 * Create a report template.
 * POST /api/v1/report-templates/
 */
export function createReportTemplate(name, filePath) {
  return request.post('/report-templates/', { name, file_path: filePath })
}

/**
 * Set a template as active.
 * PUT /api/v1/report-templates/{id}/active
 */
export function setActiveTemplate(templateId) {
  return request.put(`/report-templates/${templateId}/active`)
}

/**
 * Delete a report template.
 * DELETE /api/v1/report-templates/{id}
 */
export function deleteReportTemplate(templateId) {
  return request.delete(`/report-templates/${templateId}`)
}

// ==================== Evaluation Standard Knowledge ====================

/**
 * List all evaluation standard knowledge entries.
 * GET /api/v1/evaluation-standard-knowledge/
 */
export function listKnowledgeEntries() {
  return request.get('/evaluation-standard-knowledge/')
}

/**
 * Get a single knowledge entry.
 * GET /api/v1/evaluation-standard-knowledge/{id}
 */
export function getKnowledgeEntry(id) {
  return request.get(`/evaluation-standard-knowledge/${id}`)
}

/**
 * Create a knowledge entry.
 * POST /api/v1/evaluation-standard-knowledge/
 */
export function createKnowledgeEntry(data) {
  return request.post('/evaluation-standard-knowledge/', data)
}

/**
 * Update a knowledge entry.
 * PUT /api/v1/evaluation-standard-knowledge/{id}
 */
export function updateKnowledgeEntry(id, data) {
  return request.put(`/evaluation-standard-knowledge/${id}`, data)
}

/**
 * Delete a knowledge entry.
 * DELETE /api/v1/evaluation-standard-knowledge/{id}
 */
export function deleteKnowledgeEntry(id) {
  return request.delete(`/evaluation-standard-knowledge/${id}`)
}

// ==================== Component Batch Update ====================

/**
 * Batch update component checks.
 * PUT /api/v1/components/batch
 */
export function batchUpdateComponents(items) {
  return request.put('/components/batch', { items })
}
