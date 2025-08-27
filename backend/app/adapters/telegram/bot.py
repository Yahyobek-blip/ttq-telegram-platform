from __future__ import annotations

import json
import logging
import os
from typing import Any, List, Optional

import aiohttp
from aiogram import Router, types
from aiogram.filters import Command

logger = logging.getLogger("tg_bot")
router = Router(name="tg-bot")

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://backend:8080").rstrip("/")


def _short_json(obj: Any) -> str:
    try:
        s = json.dumps(obj, ensure_ascii=False)
        return s if len(s) <= 400 else s[:397] + "..."
    except Exception:
        return str(obj)


async def _request_json(
    method: str, path: str, *, json_body: Any | None = None, timeout: int = 15
) -> Any:
    url = (
        path
        if path.startswith("http")
        else f"{BACKEND_BASE_URL}{path if path.startswith('/') else '/'+path}"
    )
    async with aiohttp.ClientSession() as sess:
        async with sess.request(method, url, json=json_body, timeout=timeout) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"{resp.status} {text}")
            try:
                return json.loads(text)
            except Exception:
                return {"raw": text}


async def _get_user_by_tg(tg_user_id: int) -> Optional[dict]:
    data = await _request_json("GET", f"/api/v1/users?tg_user_id={tg_user_id}")
    logger.info(
        "tg_bot:/me raw resp type=%s val=%s", type(data).__name__.lower(), _short_json(data)
    )
    users: List[dict] = data if isinstance(data, list) else (data.get("items") or [])
    return users[0] if users else None


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Привет! ✌️\n"
        "Команды:\n"
        "• /help — помощь\n"
        "• /ping — пинг backend\n"
        "• /id — показать мой Telegram ID\n"
        "• /link — создать/синхронизировать профиль в БД\n"
        "• /me — мой профиль + членства\n"
        "• /orgs — мои организации и роли\n"
        "• /setname Имя Фамилия — обновить display_name в БД\n"
        "• /demo <text> [steps] [delay] — запустить Celery long_demo\n"
        "• /status <task_id> — статус Celery-задачи\n"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await cmd_start(message)


@router.message(Command("ping"))
async def cmd_ping(message: types.Message) -> None:
    try:
        data = await _request_json("GET", "/api/v1/ping", timeout=5)
        await message.answer(f"backend ответил: {json.dumps(data, ensure_ascii=False)}")
    except Exception as e:
        await message.answer(f"ошибка запроса к backend: {e!r}")


@router.message(Command("id"))
async def cmd_id(message: types.Message) -> None:
    await message.answer(f"Ваш Telegram ID: {message.from_user.id}")


@router.message(Command("me"))
async def cmd_me(message: types.Message) -> None:
    try:
        user = await _get_user_by_tg(message.from_user.id)
        if not user:
            await message.answer("В БД тебя пока нет. Нажми /link — создам/синхронизирую профиль.")
            return

        lines = [
            "Профиль в БД:",
            f"id: {user.get('id')}",
            f"tg_user_id: {user.get('tg_user_id')}",
            f"display_name: {user.get('display_name')}",
            f"is_active: {user.get('is_active')}",
        ]

        memberships = await _request_json("GET", f"/api/v1/org-users?user_id={user.get('id')}")
        if isinstance(memberships, list) and memberships:
            lines.append("\nЧленства:")
            for m in memberships:
                lines.append(f"- org_id={m.get('organization_id')} role={m.get('role')}")
        else:
            lines.append("\nЧленства: нет")

        await message.answer("\n".join(lines))
    except Exception as e:
        await message.answer(f"ошибка запроса к backend: {e!r}")


@router.message(Command("orgs"))
async def cmd_orgs(message: types.Message) -> None:
    try:
        user = await _get_user_by_tg(message.from_user.id)
        if not user:
            await message.answer("Тебя нет в БД. Нажми /link, чтобы создать запись.")
            return

        memberships = await _request_json("GET", f"/api/v1/org-users?user_id={user.get('id')}")
        if not (isinstance(memberships, list) and memberships):
            await message.answer("У тебя пока нет членств в организациях.")
            return

        lines = ["Твои организации:"]
        for m in memberships:
            lines.append(f"- org_id={m.get('organization_id')}  role={m.get('role')}")
        await message.answer("\n".join(lines))
    except Exception as e:
        await message.answer(f"ошибка запроса к backend: {e!r}")


@router.message(Command("link"))
async def cmd_link(message: types.Message) -> None:
    payload = {
        "tg_user_id": message.from_user.id,
        "display_name": message.from_user.full_name or message.from_user.username or "User",
    }
    try:
        data = await _request_json("POST", "/api/v1/users/telegram-sync", json_body=payload)
        created = data.get("created")
        user = data.get("user") or {}
        membership = data.get("membership")

        msg = [
            "Синхронизация завершена.",
            f"created: {created}",
            f"user.id: {user.get('id')}",
            f"user.display_name: {user.get('display_name')}",
            f"user.is_active: {user.get('is_active')}",
        ]
        if membership:
            msg.append(f"membership.org_id: {membership.get('org_id')}")
            msg.append(f"membership.role: {membership.get('role')}")
        await message.answer("\n".join(msg))
    except Exception as e:
        await message.answer(f"ошибка запроса к backend: {e!r}")


@router.message(Command("setname"))
async def cmd_setname(message: types.Message) -> None:
    raw = (message.text or "").split(maxsplit=1)
    if len(raw) < 2 or not raw[1].strip():
        await message.answer("Использование: /setname Имя Фамилия")
        return
    new_name = raw[1].strip()

    try:
        user = await _get_user_by_tg(message.from_user.id)
        if not user:
            await message.answer("Тебя нет в БД. Нажми сначала /link.")
            return

        user_id = user.get("id")
        data = await _request_json(
            "PATCH", f"/api/v1/users/{user_id}", json_body={"display_name": new_name}
        )
        updated_name = data.get("display_name")
        await message.answer(f"Готово. Новое имя: {updated_name}")
    except Exception as e:
        await message.answer(f"ошибка PATCH /users: {e!r}")


@router.message(Command("demo"))
async def cmd_demo(message: types.Message) -> None:
    """
    /demo <text> [steps] [delay]
    Примеры:
      /demo hello
      /demo привет 5 0.2
    """
    parts = (message.text or "").split(maxsplit=3)
    if len(parts) < 2:
        await message.answer("Использование: /demo <text> [steps] [delay]")
        return

    text = parts[1]
    steps = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 3
    try:
        delay = float(parts[3]) if len(parts) >= 4 else 0.5
    except Exception:
        delay = 0.5

    try:
        payload = {
            "task_name": "long_demo",
            "kwargs": {"text": text, "steps": steps, "delay": delay},
        }
        resp = await _request_json("POST", "/api/v1/tasks/enqueue", json_body=payload)
        tid = resp.get("task_id")
        # без parse_mode, чтобы не падать из-за символов Markdown
        await message.answer(f"Поставил задачу long_demo\nTask ID: {tid}\nСмотри /status {tid}")
    except Exception as e:
        await message.answer(f"ошибка enqueue: {e!r}")


@router.message(Command("status"))
async def cmd_status(message: types.Message) -> None:
    """
    /status <task_id>
    """
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("Использование: /status <task_id>")
        return
    tid = parts[1].strip()

    try:
        st = await _request_json("GET", f"/api/v1/tasks/{tid}/status")
        state = st.get("state")
        pct = st.get("progress_pct")
        step = st.get("step")
        total = st.get("total")
        await message.answer(f"Статус: {state}  ({pct}%)  step={step}/{total}")
    except Exception as e:
        await message.answer(f"ошибка status: {e!r}")
