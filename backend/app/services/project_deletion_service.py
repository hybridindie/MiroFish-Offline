"""
Project Deletion Service
Orchestrates safe, atomic project deletion including reports, simulations, and graph.
"""

from typing import Optional
from dataclasses import dataclass
from flask import current_app

from .simulation_manager import SimulationManager
from .simulation_runner import SimulationRunner
from .report_agent import ReportManager
from ..models.project import ProjectManager
from ..utils.logger import get_logger

logger = get_logger('mirofish.project_deletion')


@dataclass
class DeletionResult:
    """Result of a project deletion operation."""
    success: bool
    project_id: str
    graph_deleted: bool = False
    deleted_simulations: int = 0
    deleted_reports: int = 0
    error: Optional[str] = None


class ProjectDeletionService:
    """
    Handles safe, orchestrated deletion of projects including:
    - Reports linked to simulations
    - Simulations and their runtime artifacts
    - Graph data in Neo4j
    - Project metadata
    """

    def delete_project(self, project_id: str) -> DeletionResult:
        """
        Delete a project and all associated data.
        
        Validates preconditions (no active simulations, Neo4j availability)
        before making any destructive changes. Returns detailed deletion results.
        
        Args:
            project_id: The ID of the project to delete.
            
        Returns:
            DeletionResult with success status and deletion counts.
        """
        # Precondition: Retrieve project and validate it exists.
        project = ProjectManager.get_project(project_id)
        if not project:
            return DeletionResult(
                success=False,
                project_id=project_id,
                error=f"Project does not exist: {project_id}"
            )

        # Precondition 1: Check for Neo4j availability *before* any deletions.
        storage = current_app.extensions.get('neo4j_storage')
        neo4j_available = storage is not None
        
        # Precondition 2: Check for active simulations.
        active_simulations = self._get_active_simulations(project_id)
        if active_simulations:
            return DeletionResult(
                success=False,
                project_id=project_id,
                error=(
                    "Cannot delete project while simulations are running. "
                    f"Stop these simulations first: {', '.join(active_simulations)}"
                )
            )

        # If Neo4j is unavailable, fail early rather than leaving partial state.
        if not neo4j_available and project.graph_id:
            return DeletionResult(
                success=False,
                project_id=project_id,
                error="GraphStorage not initialized — check Neo4j connection"
            )

        # All preconditions passed; proceed with deletion in order.
        deleted_reports = self._delete_reports(project_id)
        deleted_simulations = self._delete_simulations(project_id)
        deleted_graph = self._delete_graph(project_id, project.graph_id) if neo4j_available else False

        # If the project had a graph but deletion failed, stop here to avoid
        # orphaning the graph data in Neo4j.
        if project.graph_id and not deleted_graph:
            return DeletionResult(
                success=False,
                project_id=project_id,
                error=(
                    f"Graph deletion failed for graph '{project.graph_id}'; "
                    "project metadata was preserved to allow retry"
                )
            )

        # Final: Delete project metadata.
        success = ProjectManager.delete_project(project_id)

        if not success:
            return DeletionResult(
                success=False,
                project_id=project_id,
                error=f"Project metadata deletion failed: {project_id}"
            )

        return DeletionResult(
            success=True,
            project_id=project_id,
            graph_deleted=deleted_graph,
            deleted_simulations=deleted_simulations,
            deleted_reports=deleted_reports
        )

    def _get_active_simulations(self, project_id: str) -> list[str]:
        """
        Identify simulations currently running for this project.
        
        Returns:
            List of simulation IDs with active/running status.
        """
        manager = SimulationManager()
        simulations = manager.list_simulations(project_id=project_id)
        
        active_statuses = {"starting", "running", "stopping"}
        active_sims = []
        
        for sim in simulations:
            run_state = SimulationRunner.get_run_state(sim.simulation_id)
            if run_state and run_state.runner_status.value in active_statuses:
                active_sims.append(sim.simulation_id)
        
        return active_sims

    def _delete_reports(self, project_id: str) -> int:
        """
        Delete all reports linked to simulations in this project.
        
        Uses batch deletion to avoid orphaned data. Returns count deleted.
        """
        manager = SimulationManager()
        simulations = manager.list_simulations(project_id=project_id)
        
        deleted_count = 0
        for sim in simulations:
            # Delete reports in batches to avoid memory bloat.
            while True:
                reports = ReportManager.list_reports(
                    simulation_id=sim.simulation_id, 
                    limit=200
                )
                if not reports:
                    break

                deleted_in_batch = 0
                for report in reports:
                    if ReportManager.delete_report(report.report_id):
                        deleted_count += 1
                        deleted_in_batch += 1

                # Guard against infinite loops if deletion repeatedly fails.
                if deleted_in_batch == 0:
                    break
        
        return deleted_count

    def _delete_simulations(self, project_id: str) -> int:
        """
        Delete all simulations and their runtime artifacts for this project.
        
        Cleans up runtime state before deleting simulation metadata.
        """
        manager = SimulationManager()
        simulations = manager.list_simulations(project_id=project_id)
        
        for sim in simulations:
            SimulationRunner.cleanup_simulation_runtime(sim.simulation_id)
        
        return manager.delete_simulations_by_project(project_id)

    def _delete_graph(self, project_id: str, graph_id: Optional[str]) -> bool:
        """
        Delete the graph from Neo4j storage.
        
        Returns True if deleted successfully, False if no graph or error.
        """
        if not graph_id:
            return False
        
        try:
            storage = current_app.extensions.get('neo4j_storage')
            if storage:
                storage.delete_graph(graph_id)
                return True
        except Exception as e:
            logger.error(
                "Failed to delete graph '%s' for project '%s': %s",
                graph_id,
                project_id,
                e
            )
        
        return False
