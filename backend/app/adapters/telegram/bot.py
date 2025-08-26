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


async def _backend_json(
    method: str, url: str, *, json_body: Any | None = None, timeout: int = 10
) -> Any:
    async with aiohttp.ClientSession() as sess:
        if method == "GET":
            async with sess.get(url, timeout=timeout) as resp:
                return await resp.json(content_type=None)
        elif method == "POST":
            async with sess.post(url, json=json_body, timeout=timeout) as resp:
                return await resp.json(content_type=None)
        elif method == "PATCH":
            async with sess.patch(url, json=json_body, timeout=timeout) as resp:
                return await resp.json(content_type=None)
        else:
            raise RuntimeError(f"unsupported method: {method}")


async def _get_user_by_tg(tg_user_id: int) -> Optional[dict]:
    url = f"{BACKEND_BASE_URL}/api/v1/users?tg_user_id={tg_user_id}"
    data = await _backend_json("GET", url)
    logger.info(
        "tg_bot:/me raw resp type=%s val=%s", type(data).__name__.lower(), _short_json(data)
    )
    users: List[dict] = data if isinstance(data, list) else data.get("items") or []
    return users[0] if users else None


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(
        "Привет! ✌️\n"
        "Команды:\n"
        "• /help — помощь\n"
        "• /ping — пинг backend\n"
        "• /link — создать/синхронизировать профиль в БД\n"
        "• /me — показать мой профиль + членства\n"
        "• /orgs — мои организации и роли\n"
        "• /id — показать мой Telegram ID\n"
        "• /setname Имя Фамилия — обновить display_name в БД\n"
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer(
        "Доступные команды:\n"
        "/ping — проверить связь с backend\n"
        "/link — синхронизировать профиль по Telegram ID\n"
        "/me — профиль в БД + членства\n"
        "/orgs — показать мои организации и роли\n"
        "/id — показать мой Telegram ID\n"
        "/setname Имя Фамилия — обновить display_name\n"
    )


@router.message(Command("ping"))
async def cmd_ping(message: types.Message) -> None:
    url = f"{BACKEND_BASE_URL}/api/v1/ping"
    try:
        data = await _backend_json("GET", url, timeout=5)
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

        # профиль
        lines = [
            "Профиль в БД:",
            f"id: {user.get('id')}",
            f"tg_user_id: {user.get('tg_user_id')}",
            f"display_name: {user.get('display_name')}",
            f"is_active: {user.get('is_active')}",
        ]

        # членства
        orgs_url = f"{BACKEND_BASE_URL}/api/v1/org-users?user_id={user.get('id')}"
        memberships = await _backend_json("GET", orgs_url)
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

        orgs_url = f"{BACKEND_BASE_URL}/api/v1/org-users?user_id={user.get('id')}"
        memberships = await _backend_json("GET", orgs_url)

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
        # "username": message.from_user.username,
        # "language_code": message.from_user.language_code,
        # "is_premium": getattr(message.from_user, "is_premium", None),
    }
    url = f"{BACKEND_BASE_URL}/api/v1/users/telegram-sync"
    try:
        data = await _backend_json("POST", url, json_body=payload)
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
    # парсим аргументы после команды
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
        url = f"{BACKEND_BASE_URL}/api/v1/users/{user_id}"
        data = await _backend_json("PATCH", url, json_body={"display_name": new_name})
        await message.answer(f"Готово. Новое имя: {data.get('display_name')}")
    except Exception as e:
        await message.answer(f"ошибка запроса к backend: {e!r}")
