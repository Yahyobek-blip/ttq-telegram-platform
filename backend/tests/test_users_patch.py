# tests/test_users_patch.py
import random
from uuid import uuid4


def test_users_patch_display_name(client):
    # 1) создаём орг (чтобы telegram-sync мог при желании привязать членство)
    org_name = f"Org QA {uuid4().hex[:8]}"
    org = client.post("/api/v1/organizations", json={"name": org_name}).json()
    assert "id" in org

    # 2) создаём/синхронизируем юзера
    tg_id = 6_900_000_000 + random.randint(10_000, 99_999)
    sync = client.post(
        "/api/v1/users/telegram-sync",
        json={"tg_user_id": tg_id, "display_name": "Old Name"},
    ).json()
    user = sync["user"]
    user_id = user["id"]

    # 3) PATCH — меняем display_name
    new_name = "New Display Name"
    patched = client.patch(f"/api/v1/users/{user_id}", json={"display_name": new_name})
    assert patched.status_code == 200, patched.text
    assert patched.json()["display_name"] == new_name
