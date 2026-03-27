<template>
  <div class="project-manager">
    <div class="pm-header">
      <div class="pm-title-section">
        <span class="pm-icon">◇</span>
        <span class="pm-title">Project Manager</span>
        <span class="pm-project-count" v-if="projects.length > 0">({{ projects.length }})</span>
      </div>
      <div class="pm-header-actions">
        <button 
          class="pm-refresh-btn"
          @click="loadProjects"
          :disabled="loading"
          title="Refresh project list"
        >
          <span v-if="loading">↻</span>
          <span v-else>↻</span>
        </button>
        <button 
          v-if="projects.length > 0"
          class="pm-toggle-btn"
          @click="isExpanded = !isExpanded"
          :title="isExpanded ? 'Collapse' : 'Expand'"
        >
          {{ isExpanded ? '−' : '+' }}
        </button>
      </div>
    </div>

    <Transition name="expand">
      <div v-if="isExpanded" class="pm-content">
        <!-- Search/Filter bar -->
        <div class="pm-search-bar">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search projects by name or ID..."
            class="pm-search-input"
          />
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="pm-loading">
          <span class="pm-spinner"></span>
          <span class="pm-loading-text">Loading projects...</span>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="pm-error">
          <span class="pm-error-icon">⚠</span>
          <div class="pm-error-content">
            <span class="pm-error-text">{{ error }}</span>
            <button @click="loadProjects" class="pm-error-retry">
              Retry
            </button>
          </div>
        </div>

        <!-- No projects -->
        <div v-else-if="filteredProjects.length === 0" class="pm-empty">
          <span class="pm-empty-icon">◇</span>
          <span class="pm-empty-text">No projects found</span>
        </div>

        <!-- Projects list -->
        <div v-else class="pm-list">
          <div
            v-for="project in filteredProjects"
            :key="project.project_id"
            class="pm-item"
            :class="{ 'pm-item-loading': deletingId === project.project_id }"
          >
            <div class="pm-item-info">
              <div class="pm-item-id">{{ project.project_id }}</div>
              <div class="pm-item-name">{{ project.name || 'Untitled Project' }}</div>
              <div class="pm-item-status" :class="`status-${project.status}`">
                {{ formatStatus(project.status) }}
              </div>
              <div class="pm-item-date">{{ formatDate(project.created_at) }}</div>
            </div>

            <div class="pm-item-actions">
              <button
                class="pm-action-btn pm-btn-resume"
                @click.stop="resumeProject(project)"
                title="Continue working on this project"
                :disabled="deletingId === project.project_id"
              >
                <span class="pm-btn-icon">→</span>
                <span class="pm-btn-label">Resume</span>
              </button>
              <button
                class="pm-action-btn pm-btn-reset"
                @click.stop="resetProjectClick(project)"
                title="Reset project (clear graph, keep ontology)"
                :disabled="deletingId === project.project_id || !project.graph_id"
              >
                <span class="pm-btn-icon">↻</span>
                <span class="pm-btn-label">Reset</span>
              </button>
              <button
                class="pm-action-btn pm-btn-delete"
                @click.stop="deleteProjectClick(project)"
                title="Delete this project"
                :disabled="deletingId !== null && deletingId !== project.project_id"
              >
                <span v-if="deletingId === project.project_id" class="pm-btn-spinner"></span>
                <span v-else class="pm-btn-icon">×</span>
                <span class="pm-btn-label">{{ deletingId === project.project_id ? 'Deleting...' : 'Delete' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Confirmation Modal for Delete/Reset -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="confirmModal.show" class="pm-modal-overlay" @click.self="closeModal">
          <div class="pm-modal-content">
            <div class="pm-modal-header">
              <span>{{ confirmModal.title }}</span>
              <button class="pm-modal-close" @click="closeModal">×</button>
            </div>
            <div class="pm-modal-body">
              <p>{{ confirmModal.message }}</p>
              <p v-if="confirmModal.projectId" class="pm-project-highlight">
                Project ID: <strong>{{ confirmModal.projectId }}</strong>
              </p>
            </div>
            <div class="pm-modal-actions">
              <button class="pm-modal-btn pm-btn-cancel" @click="closeModal">Cancel</button>
              <button
                class="pm-modal-btn pm-btn-confirm"
                :class="confirmModal.isDelete ? 'pm-btn-delete' : 'pm-btn-reset'"
                @click="confirmAction"
                :disabled="confirmModal.isLoading"
              >
                {{ confirmModal.isLoading ? 'Processing...' : confirmModal.action }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listProjects, deleteProject, resetProject } from '../api/projectManager'

const router = useRouter()

// State
const projects = ref([])
const loading = ref(false)
const error = ref('')
const isExpanded = ref(true)
const searchQuery = ref('')
const deletingId = ref(null)

// Confirmation modal state
const confirmModal = ref({
  show: false,
  title: '',
  message: '',
  action: '',
  projectId: '',
  isDelete: false,
  isLoading: false,
  callback: null
})

// Filtered projects based on search
const filteredProjects = computed(() => {
  if (!searchQuery.value.trim()) return projects.value
  
  const query = searchQuery.value.toLowerCase()
  return projects.value.filter(p =>
    p.project_id.toLowerCase().includes(query) ||
    (p.name && p.name.toLowerCase().includes(query))
  )
})

// Load projects on mount
onMounted(() => {
  loadProjects()
})

// Functions
async function loadProjects() {
  loading.value = true
  error.value = ''
  try {
    const response = await listProjects()
    if (response.success) {
      projects.value = response.data || []
    } else {
      error.value = 'Failed to load projects'
    }
  } catch (err) {
    error.value = err.message || 'Error loading projects'
    console.error('Failed to load projects:', err)
  } finally {
    loading.value = false
  }
}

function resumeProject(project) {
  router.push({
    name: 'MainView',
    params: { projectId: project.project_id }
  })
}

function resetProjectClick(project) {
  confirmModal.value = {
    show: true,
    title: 'Reset Project',
    message: 'This will clear the graph and reset the project to the ontology stage. The project can be rebuilt from the ontology.',
    action: 'Reset',
    projectId: project.project_id,
    isDelete: false,
    isLoading: false,
    callback: () => performReset(project.project_id)
  }
}

function deleteProjectClick(project) {
  confirmModal.value = {
    show: true,
    title: 'Delete Project',
    message: 'This action cannot be undone. All project data including the graph, ontology, and associated files will be permanently deleted.',
    action: 'Delete',
    projectId: project.project_id,
    isDelete: true,
    isLoading: false,
    callback: () => performDelete(project.project_id)
  }
}

async function confirmAction() {
  confirmModal.value.isLoading = true
  try {
    await confirmModal.value.callback()
  } catch (err) {
    error.value = err.message || 'Operation failed'
    console.error('Operation failed:', err)
  } finally {
    confirmModal.value.isLoading = false
    closeModal()
  }
}

async function performDelete(projectId) {
  deletingId.value = projectId
  try {
    const response = await deleteProject(projectId)
    if (response.success) {
      projects.value = projects.value.filter(p => p.project_id !== projectId)
    } else {
      throw new Error(response.error || 'Failed to delete project')
    }
  } finally {
    deletingId.value = null
  }
}

async function performReset(projectId) {
  try {
    const response = await resetProject(projectId)
    if (response.success) {
      const idx = projects.value.findIndex(p => p.project_id === projectId)
      if (idx !== -1) {
        projects.value[idx] = response.data
      }
    } else {
      throw new Error(response.error || 'Failed to reset project')
    }
  } catch (err) {
    throw err
  }
}

function closeModal() {
  confirmModal.value.show = false
}

function formatStatus(status) {
  const statusMap = {
    'CREATED': 'Created',
    'ONTOLOGY_GENERATED': 'Ontology Ready',
    'GRAPH_BUILDING': 'Building Graph',
    'GRAPH_COMPLETE': 'Graph Ready',
    'ENVIRONMENT_SETUP': 'Environment Setup',
    'SIMULATION_READY': 'Ready to Simulate',
    'ERROR': 'Error'
  }
  return statusMap[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>

<style scoped>
.project-manager {
  border-top: 1px solid rgba(255, 165, 0, 0.3);
  padding: 24px;
  background: linear-gradient(135deg, rgba(255, 165, 0, 0.02) 0%, rgba(100, 200, 255, 0.02) 100%);
}

.pm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  cursor: pointer;
}

.pm-title-section {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.pm-icon {
  color: #ffa500;
}

.pm-project-count {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}

.pm-header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pm-refresh-btn {
  background: rgba(255, 165, 0, 0.1);
  border: 1px solid rgba(255, 165, 0, 0.3);
  color: #ffa500;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pm-refresh-btn:hover:not(:disabled) {
  background: rgba(255, 165, 0, 0.2);
  border-color: rgba(255, 165, 0, 0.5);
}

.pm-refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pm-refresh-btn:disabled {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.pm-toggle-btn {
  background: rgba(255, 165, 0, 0.1);
  border: 1px solid rgba(255, 165, 0, 0.3);
  color: #ffa500;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pm-toggle-btn:hover {
  background: rgba(255, 165, 0, 0.2);
  border-color: rgba(255, 165, 0, 0.5);
}

.pm-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pm-search-bar {
  display: flex;
}

.pm-search-input {
  flex: 1;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 165, 0, 0.2);
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  transition: all 0.2s ease;
}

.pm-search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.pm-search-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 165, 0, 0.5);
}

.pm-loading,
.pm-error,
.pm-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.pm-spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 165, 0, 0.2);
  border-top-color: #ffa500;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pm-error {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 4px;
  color: #ff6b6b;
}

.pm-error-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.pm-error-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.pm-error-text {
  font-size: 14px;
}

.pm-error-retry {
  align-self: flex-start;
  font-size: 12px;
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
  padding: 4px 10px;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pm-error-retry:hover {
  background: rgba(255, 107, 107, 0.3);
  border-color: rgba(255, 107, 107, 0.7);
}

.pm-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.pm-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 165, 0, 0.1);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.pm-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 165, 0, 0.3);
}

.pm-item-loading {
  opacity: 0.6;
}

.pm-item-info {
  flex: 1;
}

.pm-item-id {
  font-size: 12px;
  color: rgba(255, 165, 0, 0.8);
  font-weight: 600;
  margin-bottom: 4px;
}

.pm-item-name {
  font-size: 14px;
  color: #fff;
  font-weight: 500;
  margin-bottom: 4px;
}

.pm-item-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  margin-right: 8px;
}

.status-CREATED,
.status-ONTOLOGY_GENERATED {
  background: rgba(100, 200, 255, 0.2);
  color: #64c8ff;
}

.status-GRAPH_BUILDING {
  background: rgba(255, 165, 0, 0.2);
  color: #ffa500;
}

.status-GRAPH_COMPLETE,
.status-SIMULATION_READY {
  background: rgba(100, 255, 150, 0.2);
  color: #64ff96;
}

.status-ERROR {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.pm-item-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.pm-item-actions {
  display: flex;
  gap: 8px;
  margin-left: 12px;
}

.pm-action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: 1px solid;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.pm-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pm-btn-resume {
  background: rgba(100, 200, 255, 0.1);
  border-color: rgba(100, 200, 255, 0.3);
  color: #64c8ff;
}

.pm-btn-resume:hover:not(:disabled) {
  background: rgba(100, 200, 255, 0.2);
  border-color: rgba(100, 200, 255, 0.5);
}

.pm-btn-reset {
  background: rgba(255, 165, 0, 0.1);
  border-color: rgba(255, 165, 0, 0.3);
  color: #ffa500;
}

.pm-btn-reset:hover:not(:disabled) {
  background: rgba(255, 165, 0, 0.2);
  border-color: rgba(255, 165, 0, 0.5);
}

.pm-btn-delete {
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
}

.pm-btn-delete:hover:not(:disabled) {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.5);
}

.pm-btn-icon {
  font-size: 14px;
}

.pm-btn-spinner {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.pm-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.pm-modal-content {
  background: #1a1a1a;
  border: 1px solid rgba(255, 165, 0, 0.3);
  border-radius: 8px;
  padding: 24px;
  max-width: 400px;
  min-width: 300px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9);
}

.pm-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #fff;
}

.pm-modal-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.pm-modal-close:hover {
  color: #fff;
}

.pm-modal-body {
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.pm-modal-body p {
  margin: 8px 0;
  line-height: 1.5;
}

.pm-project-highlight {
  background: rgba(255, 165, 0, 0.1);
  padding: 8px;
  border-radius: 4px;
  border-left: 2px solid #ffa500;
  margin-top: 12px;
}

.pm-modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.pm-modal-btn {
  padding: 8px 16px;
  border: 1px solid;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pm-btn-cancel {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.pm-btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.pm-btn-confirm {
  color: #fff;
}

.pm-btn-confirm.pm-btn-reset {
  background: rgba(255, 165, 0, 0.2);
  border-color: rgba(255, 165, 0, 0.5);
  color: #ffa500;
}

.pm-btn-confirm.pm-btn-reset:hover {
  background: rgba(255, 165, 0, 0.3);
}

.pm-btn-confirm.pm-btn-delete {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.5);
  color: #ff6b6b;
}

.pm-btn-confirm.pm-btn-delete:hover {
  background: rgba(255, 107, 107, 0.3);
}

/* Transitions */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .pm-modal-content,
.modal-leave-active .pm-modal-content {
  transition: transform 0.2s ease;
}

.modal-enter-from .pm-modal-content,
.modal-leave-to .pm-modal-content {
  transform: scale(0.95);
}

/* Scrollbar styling */
.pm-list::-webkit-scrollbar {
  width: 6px;
}

.pm-list::-webkit-scrollbar-track {
  background: transparent;
}

.pm-list::-webkit-scrollbar-thumb {
  background: rgba(255, 165, 0, 0.3);
  border-radius: 3px;
}

.pm-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 165, 0, 0.5);
}
</style>
