/**
 * AI API module for uniapp-house-safety.
 * Covers AI reasoning, text generation, and assistant chat.
 */
import request from './request'

// ==================== AI Reasoning ====================

/**
 * AI reasoning — structured assessment conclusion.
 * POST /api/v1/ai/reason
 */
export function aiReason(surveyId, surveyInfo, components) {
  return request.post('/ai/reason', {
    survey_id: surveyId,
    survey_info: surveyInfo,
    components: components
  })
}

/**
 * AI reasoning — streaming.
 * POST /api/v1/ai/reason/stream
 */
export function aiReasonStream(surveyId) {
  return request.post('/ai/reason/stream', { survey_id: surveyId })
}

// ==================== AI Text Generation ====================

/**
 * Generate usage history text.
 * POST /api/v1/ai/text/usage-history
 */
export function generateUsageHistory(historyChange, usageStatus, purposeInfo) {
  return request.post('/ai/text/usage-history', {
    historyChange,
    usageStatus,
    purposeInfo
  })
}

/**
 * Generate external environment description.
 * POST /api/v1/ai/text/external-environment
 */
export function generateExternalEnvironment(surroundingEnvironment, surroundingEnvironmentDesc) {
  return request.post('/ai/text/external-environment', {
    surroundingEnvironment,
    surroundingEnvironmentDesc
  })
}

/**
 * Generate structure condition description.
 * POST /api/v1/ai/text/structure-condition
 */
export function generateStructureCondition(structureInfo, basicInfo) {
  return request.post('/ai/text/structure-condition', {
    structureInfo,
    basicInfo
  })
}

/**
 * Generate remarks.
 * POST /api/v1/ai/text/remarks
 */
export function generateRemarks() {
  return request.post('/ai/text/remarks', {})
}

/**
 * Generate evaluation standards.
 * POST /api/v1/ai/text/evaluation-standards
 */
export function generateEvaluationStandards(buildingInfo) {
  return request.post('/ai/text/evaluation-standards', { buildingInfo })
}

/**
 * Generate damage summary.
 * POST /api/v1/ai/text/damage-summary
 */
export function generateDamageSummary(buildingProfile, componentChecks) {
  return request.post('/ai/text/damage-summary', {
    buildingProfile,
    componentChecks
  })
}

/**
 * Generate cause analysis.
 * POST /api/v1/ai/text/cause-analysis
 */
export function generateCauseAnalysis(buildingProfile, componentChecks) {
  return request.post('/ai/text/cause-analysis', {
    buildingProfile,
    componentChecks
  })
}

/**
 * Generate assessment conclusion.
 * POST /api/v1/ai/text/conclusion
 */
export function generateConclusion(buildingProfile, componentChecks) {
  return request.post('/ai/text/conclusion', {
    buildingProfile,
    componentChecks
  })
}

/**
 * Generate handling suggestions.
 * POST /api/v1/ai/text/handling-suggestion
 */
export function generateHandlingSuggestion(buildingProfile, componentChecks) {
  return request.post('/ai/text/handling-suggestion', {
    buildingProfile,
    componentChecks
  })
}

/**
 * Determine safety level (A/B/C/D).
 * POST /api/v1/ai/text/safety-level
 */
export function generateSafetyLevel(buildingProfile, componentChecks) {
  return request.post('/ai/text/safety-level', {
    buildingProfile,
    componentChecks
  })
}

/**
 * Generate main test content.
 * POST /api/v1/ai/text/main-test-content
 */
export function generateMainTestContent(buildingProfile) {
  return request.post('/ai/text/main-test-content', {
    buildingProfile
  })
}

/**
 * Generate applicable test standards.
 * POST /api/v1/ai/text/test-standards
 */
export function generateTestStandards(mainTestContent) {
  return request.post('/ai/text/test-standards', {
    mainTestContent
  })
}

/**
 * Generate test results summary.
 * POST /api/v1/ai/text/test-results
 */
export function generateTestResults(buildingProfile, mainTestContent, testStandards, componentChecks) {
  return request.post('/ai/text/test-results', {
    buildingProfile,
    mainTestContent,
    testStandards,
    componentChecks
  })
}

// ==================== AI Assistant Chat ====================

/**
 * Chat with the AI report modification assistant (non-streaming).
 * POST /api/v1/ai/assistant/chat
 */
export function aiAssistantChat(conversationId, message, reportContent) {
  return request.post('/ai/assistant/chat', {
    conversation_id: conversationId,
    message,
    report_content: reportContent
  })
}

/**
 * Clear conversation history.
 * POST /api/v1/ai/assistant/clear
 */
export function aiAssistantClear(conversationId) {
  return request.post('/ai/assistant/clear', {
    conversation_id: conversationId
  })
}
