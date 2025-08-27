from __future__ import annotations


def test_tasks_long_demo_eager(client):
    payload = {
        "task_name": "long_demo",
        "kwargs": {"text": "hello", "steps": 3, "delay": 0.01},
    }
    r = client.post("/api/v1/tasks/enqueue", json=payload)
    assert r.status_code == 200, r.text
    task_id = r.json()["task_id"]

    # в eager-режиме обычно сразу SUCCESS
    r = client.get(f"/api/v1/tasks/{task_id}/status")
    assert r.status_code == 200
    body = r.json()
    assert body["state"] in ("SUCCESS", "PROGRESS", "STARTED"), body
    if body["state"] == "SUCCESS":
        assert body["progress_pct"] == 100
        assert body["result"]["echo"].startswith("Processed 'hello' in")
