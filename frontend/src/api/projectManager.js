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
 * Get project details
 * @param {String} projectId - Project ID
 * @returns {Promise}
 */
export function getProjectDetails(projectId) {
  return service({
    url: `/api/graph/project/${projectId}`,
    method: 'get'
  })
}

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
