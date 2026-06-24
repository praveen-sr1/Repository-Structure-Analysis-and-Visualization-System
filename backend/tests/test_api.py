"""End-to-end API tests using the FastAPI TestClient."""
from __future__ import annotations


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scan_and_graph_flow(client, sample_repo):
    # Scan the sample repository.
    scan = client.post("/api/repositories/scan", json={"path": str(sample_repo)})
    assert scan.status_code == 201
    body = scan.json()
    repo_id = body["repository"]["id"]
    assert body["nodes_created"] >= 3
    assert body["edges_created"] >= 2

    # Graph endpoint returns nodes + edges.
    graph = client.get(f"/api/repositories/{repo_id}/graph")
    assert graph.status_code == 200
    g = graph.json()
    node_ids = {n["id"] for n in g["nodes"]}
    assert {"main.py", "pkg/utils.py", "app.js"} <= node_ids
    edge_pairs = {(e["source"], e["target"]) for e in g["edges"]}
    assert ("main.py", "pkg/utils.py") in edge_pairs


def test_stats_endpoint(client, sample_repo):
    scan = client.post("/api/repositories/scan", json={"path": str(sample_repo)})
    repo_id = scan.json()["repository"]["id"]

    stats = client.get(f"/api/repositories/{repo_id}/stats")
    assert stats.status_code == 200
    s = stats.json()
    assert s["total_files"] >= 3
    assert s["total_lines"] > 0
    languages = {lang["language"] for lang in s["languages"]}
    assert "python" in languages


def test_file_metrics_endpoint(client, sample_repo):
    scan = client.post("/api/repositories/scan", json={"path": str(sample_repo)})
    repo_id = scan.json()["repository"]["id"]

    metrics = client.get(
        f"/api/repositories/{repo_id}/files/metrics",
        params={"path": "pkg/utils.py"},
    )
    assert metrics.status_code == 200
    m = metrics.json()
    assert m["num_classes"] == 1
    assert m["num_functions"] == 1
    assert m["class_names"] == ["Helper"]
    assert m["function_names"] == ["add"]


def test_file_metrics_404_for_unknown_file(client, sample_repo):
    scan = client.post("/api/repositories/scan", json={"path": str(sample_repo)})
    repo_id = scan.json()["repository"]["id"]
    resp = client.get(
        f"/api/repositories/{repo_id}/files/metrics",
        params={"path": "nope.py"},
    )
    assert resp.status_code == 404


def test_summary_endpoint_reports_unavailable_without_provider(client, sample_repo):
    scan = client.post("/api/repositories/scan", json={"path": str(sample_repo)})
    repo_id = scan.json()["repository"]["id"]

    resp = client.get(
        f"/api/repositories/{repo_id}/files/summary",
        params={"path": "main.py"},
    )
    assert resp.status_code == 200
    body = resp.json()
    # No provider configured in tests -> available is False, but call succeeds.
    assert body["available"] is False
    assert body["content_hash"]


def test_rescan_endpoint(client, sample_repo):
    scan = client.post("/api/repositories/scan", json={"path": str(sample_repo)})
    repo_id = scan.json()["repository"]["id"]

    rescan = client.post(f"/api/repositories/{repo_id}/rescan")
    assert rescan.status_code == 200
    assert rescan.json()["repository"]["id"] == repo_id


def test_scan_invalid_path_returns_404(client):
    resp = client.post(
        "/api/repositories/scan", json={"path": "/path/does/not/exist/xyz"}
    )
    assert resp.status_code == 404


def test_list_and_delete_repository(client, sample_repo):
    scan = client.post("/api/repositories/scan", json={"path": str(sample_repo)})
    repo_id = scan.json()["repository"]["id"]

    listing = client.get("/api/repositories")
    assert listing.status_code == 200
    assert any(r["id"] == repo_id for r in listing.json())

    deleted = client.delete(f"/api/repositories/{repo_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/repositories/{repo_id}").status_code == 404
