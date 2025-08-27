# tests/test_bots_api.py
from __future__ import annotations

import random
from uuid import uuid4


def test_bots_crud_and_rotate_token(client):
    # 0) вспомогательная организация (привязка бота)
    org = client.post("/api/v1/organizations", json={"name": f"BotOrg {uuid4().hex[:6]}"}).json()
    org_id = org["id"]

    # 1) создание бота
    uname = f"mybot_{uuid4().hex[:6]}"
    created = client.post("/api/v1/bots", json={"username": uname})
    assert created.status_code == 201, created.text
    bot = created.json()
    bot_id = bot["id"]
    assert bot["username"] == uname
    assert bot["is_active"] is True  # default true в модели

    # 2) частичный апдейт: tg_bot_id + org + активность
    new_tg_id = 7_800_000_000 + random.randint(1000, 9999)
    patched = client.patch(
        f"/api/v1/bots/{bot_id}",
        json={"tg_bot_id": new_tg_id, "organization_id": org_id, "is_active": True},
    ).json()
    assert patched["tg_bot_id"] == new_tg_id
    assert patched["organization_id"] == org_id
    assert patched["is_active"] is True

    # 3) ротация токена — на выходе только last4 + rotated_at
    token = "123456:ABCTOKENEXAMPLE"
    rot = client.post(f"/api/v1/bots/{bot_id}/rotate-token", json={"token": token}).json()
    assert rot["token_last4"] == token[-4:]
    assert rot["id"] == bot_id
    assert rot["token_rotated_at"]  # дата выставлена

    # 4) удалить (проверим 204)
    resp = client.delete(f"/api/v1/bots/{bot_id}")
    assert resp.status_code == 204
