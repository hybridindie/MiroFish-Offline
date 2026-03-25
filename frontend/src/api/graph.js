import service, { requestWithRetry } from './index'

/**
 * Generate ontology (upload documents and simulation requirements)
 * @param {Object} data - Contains files, simulation_requirement, project_name, etc.
 * @returns {Promise}
 */
export function generateOntology(formData) {
  // No retry: each call creates a new project on the backend.
  // timeout:0 disables the Axios timeout; the backend fallback ontology
  // ensures a response is always returned (within LLM_TIMEOUT_SECONDS).
  return service({
    url: '/api/graph/ontology/generate',
    method: 'post',
    data: formData,
    timeout: 0,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * Build graph
 * @param {Object} data - Contains project_id, graph_name, etc.
 * @returns {Promise}
 */
export function buildGraph(data) {
  // No retry: each call starts a new background build task.
  return service({
    url: '/api/graph/build',
    method: 'post',
    data
  })
}

/**
 * Query task status
 * @param {String} taskId - Task ID
 * @returns {Promise}
 */
export function getTaskStatus(taskId) {
  return service({
    url: `/api/graph/task/${taskId}`,
    method: 'get'
  })
}

/**
 * Get graph data
 * @param {String} graphId - Graph ID
 * @returns {Promise}
 */
export function getGraphData(graphId) {
  return service({
    url: `/api/graph/data/${graphId}`,
    method: 'get'
  })
}

/**
 * Get project information
 * @param {String} projectId - Project ID
 * @returns {Promise}
 */
export function getProject(projectId) {
  return service({
    url: `/api/graph/project/${projectId}`,
    method: 'get'
  })
}
