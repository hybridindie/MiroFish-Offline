import service from './index'

/**
 * List all projects
 * @param {Number} limit - Maximum number of projects to return
 * @returns {Promise}
 */
export function listProjects(limit = 50) {
  return service({
    url: '/api/graph/project/list',
    method: 'get',
    params: { limit }
  })
}

/**
 * Get project details (alias for getProject from graph.js to maintain consistent naming)
 * @param {String} projectId - Project ID
 * @returns {Promise}
 */
export { getProject as getProjectDetails } from './graph'

/**
 * Delete a project
 * @param {String} projectId - Project ID to delete
 * @returns {Promise}
 */
export function deleteProject(projectId) {
  return service({
    url: `/api/graph/project/${projectId}`,
    method: 'delete'
  })
}

/**
 * Reset a project (clear graph and return to ontology stage)
 * @param {String} projectId - Project ID to reset
 * @returns {Promise}
 */
export function resetProject(projectId) {
  return service({
    url: `/api/graph/project/${projectId}/reset`,
    method: 'post'
  })
}
