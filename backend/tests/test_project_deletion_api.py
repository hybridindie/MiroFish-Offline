from types import SimpleNamespace

import pytest
from flask import Flask

import app.api.graph as graph_api
import app.services.project_deletion_service as deletion_svc


class FakeStorage:
    def __init__(self):
        self.deleted_graph_ids = []

    def delete_graph(self, graph_id):
        self.deleted_graph_ids.append(graph_id)


class FakeSimulationManager:
    def __init__(self, simulations=None, deleted_count=0):
        self._simulations = simulations or []
        self._deleted_count = deleted_count

    def list_simulations(self, project_id=None):
        return self._simulations

    def delete_simulations_by_project(self, project_id):
        return self._deleted_count


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(graph_api.graph_bp, url_prefix="/api/graph")
    app.extensions = {}

    with app.test_client() as test_client:
        yield test_client


def test_delete_project_returns_404_when_project_missing(client, monkeypatch):
    monkeypatch.setattr(graph_api.ProjectManager, "get_project", lambda project_id: None)

    response = client.delete("/api/graph/project/proj_missing")
    payload = response.get_json()

    assert response.status_code == 404
    assert payload["success"] is False
    assert "does not exist" in payload["error"]


def test_delete_project_blocks_if_simulation_running(client, monkeypatch):
    project = SimpleNamespace(graph_id="graph_1")
    manager = FakeSimulationManager(
        simulations=[SimpleNamespace(simulation_id="sim_1")],
        deleted_count=0,
    )

    monkeypatch.setattr(graph_api.ProjectManager, "get_project", lambda project_id: project)
    monkeypatch.setattr(deletion_svc, "SimulationManager", lambda: manager)
    monkeypatch.setattr(
        deletion_svc.SimulationRunner,
        "get_run_state",
        lambda simulation_id: SimpleNamespace(runner_status=SimpleNamespace(value="running")),
    )

    deleted_called = {"called": False}

    def _delete_project(_project_id):
        deleted_called["called"] = True
        return True

    monkeypatch.setattr(graph_api.ProjectManager, "delete_project", _delete_project)

    response = client.delete("/api/graph/project/proj_1")
    payload = response.get_json()

    assert response.status_code == 409
    assert payload["success"] is False
    assert "Stop these simulations first" in payload["error"]
    assert deleted_called["called"] is False


def test_delete_project_cleans_reports_simulations_and_graph(client, monkeypatch):
    project = SimpleNamespace(graph_id="graph_1")
    simulations = [
        SimpleNamespace(simulation_id="sim_1"),
        SimpleNamespace(simulation_id="sim_2"),
    ]
    manager = FakeSimulationManager(simulations=simulations, deleted_count=2)
    storage = FakeStorage()
    client.application.extensions["neo4j_storage"] = storage

    monkeypatch.setattr(graph_api.ProjectManager, "get_project", lambda project_id: project)
    monkeypatch.setattr(graph_api.ProjectManager, "delete_project", lambda project_id: True)
    monkeypatch.setattr(deletion_svc, "SimulationManager", lambda: manager)
    monkeypatch.setattr(deletion_svc.SimulationRunner, "get_run_state", lambda simulation_id: None)

    cleaned_simulation_ids = []
    monkeypatch.setattr(
        deletion_svc.SimulationRunner,
        "cleanup_simulation_runtime",
        lambda simulation_id: cleaned_simulation_ids.append(simulation_id),
    )

    # Stateful mock: return the report only on the first call so the while-True
    # pagination loop in _delete_reports terminates after one batch.
    remaining_reports = {"sim_1": [SimpleNamespace(report_id="report_1")]}

    def _list_reports(simulation_id, limit=200):
        return list(remaining_reports.get(simulation_id, []))

    def _delete_report(report_id):
        for key in remaining_reports:
            remaining_reports[key] = [r for r in remaining_reports[key] if r.report_id != report_id]
        return True

    monkeypatch.setattr(deletion_svc.ReportManager, "list_reports", _list_reports)
    monkeypatch.setattr(deletion_svc.ReportManager, "delete_report", _delete_report)

    response = client.delete("/api/graph/project/proj_1")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["project_id"] == "proj_1"
    assert payload["data"]["graph_deleted"] is True
    assert payload["data"]["deleted_simulations"] == 2
    assert payload["data"]["deleted_reports"] == 1
    assert storage.deleted_graph_ids == ["graph_1"]
    assert cleaned_simulation_ids == ["sim_1", "sim_2"]


def test_delete_project_returns_500_when_graph_storage_missing(client, monkeypatch):
    project = SimpleNamespace(graph_id="graph_1")
    manager = FakeSimulationManager(simulations=[], deleted_count=0)
    client.application.extensions["neo4j_storage"] = None

    monkeypatch.setattr(graph_api.ProjectManager, "get_project", lambda project_id: project)
    monkeypatch.setattr(deletion_svc, "SimulationManager", lambda: manager)
    monkeypatch.setattr(deletion_svc.SimulationRunner, "get_run_state", lambda simulation_id: None)

    response = client.delete("/api/graph/project/proj_1")
    payload = response.get_json()

    assert response.status_code == 500
    assert payload["success"] is False
    assert "GraphStorage not initialized" in payload["error"]
