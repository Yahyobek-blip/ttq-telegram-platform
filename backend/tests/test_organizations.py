from __future__ import annotations


def test_orgs_crud_flow(client):
    # create
    r = client.post("/api/v1/organizations", json={"name": "Acme QA"})
    assert r.status_code == 201, r.text
    org = r.json()
    org_id = org["id"]
    assert org["name"] == "Acme QA"

    # list + filter
    r = client.get("/api/v1/organizations")
    assert r.status_code == 200
    items = r.json()
    assert any(x["id"] == org_id for x in items)

    r = client.get("/api/v1/organizations", params={"q": "Acme"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    assert any("Acme" in x["name"] for x in items)

    # get by id
    r = client.get(f"/api/v1/organizations/{org_id}")
    assert r.status_code == 200
    assert r.json()["id"] == org_id

    # patch
    r = client.patch(f"/api/v1/organizations/{org_id}", json={"name": "Acme QA (dev)"})
    assert r.status_code == 200
    assert r.json()["name"] == "Acme QA (dev)"

    # delete
    r = client.delete(f"/api/v1/organizations/{org_id}")
    assert r.status_code == 204

    # deleted → 404
    r = client.get(f"/api/v1/organizations/{org_id}")
    assert r.status_code == 404
