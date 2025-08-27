# tests/test_users_and_org_users.py
from __future__ import annotations

import random
from uuid import uuid4


def test_user_sync_and_org_membership_crud(client):
    # 1) создаём организацию
    org_name = f"Org QA {uuid4().hex[:8]}"
    org = client.post("/api/v1/organizations", json={"name": org_name}).json()
    org_id = org["id"]

    # 2) синхронизируем пользователя по Telegram ID
    tg_id = 6_900_000_000 + random.randint(10_000, 99_999)
    user_display = f"Tester {uuid4().hex[:6]}"
    sync = client.post(
        "/api/v1/users/telegram-sync",
        json={"tg_user_id": tg_id, "display_name": user_display},
    ).json()
    assert sync["created"] in (True, False)
    user_id = sync["user"]["id"]

    # 3) поиск по точному tg_user_id
    found = client.get(f"/api/v1/users?tg_user_id={tg_id}").json()
    assert isinstance(found, list) and any(u["id"] == user_id for u in found)

    # 4) создаём membership
    m = client.post(
        "/api/v1/org-users",
        json={"organization_id": org_id, "user_id": user_id, "role": "member"},
    )
    assert m.status_code == 201
    membership = m.json()
    mid = membership["id"]
    assert membership["role"] == "member"

    # 5) листинг по user_id
    lst = client.get(f"/api/v1/org-users?user_id={user_id}").json()
    assert any(x["id"] == mid for x in lst)

    # 6) апдейт роли
    upd = client.patch(f"/api/v1/org-users/{mid}", json={"role": "admin"}).json()
    assert upd["role"] == "admin"

    # 7) удаление membership (204 без тела)
    resp = client.delete(f"/api/v1/org-users/{mid}")
    assert resp.status_code == 204
