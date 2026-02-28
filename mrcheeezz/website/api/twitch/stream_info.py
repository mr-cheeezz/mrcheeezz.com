import requests

from api.credentials import get_provider_access_token, get_provider_client_id
from mrcheeezz import env
from mrcheeezz.log import logger


def _twitch_headers():
    client_id = get_provider_client_id("twitch", fallback=env.twitch_client_id)
    if not client_id:
        return None

    headers = {"Client-ID": client_id}
    access_token = get_provider_access_token("twitch", fallback="")
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def _get_json(url, headers, timeout=8):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        logger.info("Twitch API error on %s: %s", url, response.status_code)
        return None

    try:
        return response.json()
    except ValueError:
        return None


def get_stream_info(user_id):
    if not user_id:
        return {"live": False, "viewer_count": 0, "user_login": None}

    headers = _twitch_headers()
    if not headers:
        return {"live": False, "viewer_count": 0, "user_login": None}

    url = f"https://api.twitch.tv/helix/streams?user_id={user_id}"
    payload = _get_json(url, headers)
    if not payload:
        return {"live": False, "viewer_count": 0, "user_login": None}

    data = payload.get("data") or []
    if not data:
        return {"live": False, "viewer_count": 0, "user_login": None}

    stream_info = data[0]
    return {
        "live": True,
        "viewer_count": int(stream_info.get("viewer_count") or 0),
        "user_login": stream_info.get("user_login") or None,
    }


def get_username_from_id(user_id):
    if not user_id:
        return None

    headers = _twitch_headers()
    if not headers:
        return None

    url = f"https://api.twitch.tv/helix/users?id={user_id}"
    payload = _get_json(url, headers)
    if not payload:
        return None

    data = payload.get("data") or []
    if not data:
        return None

    return data[0].get("login")


def get_live_state(user_id=None):
    resolved_user_id = user_id or env.twitch_channel_id
    if not resolved_user_id:
        return {
            "is_live": False,
            "view_count": 0,
            "username": None,
            "url": None,
        }

    stream = get_stream_info(resolved_user_id)
    username = stream.get("user_login") or get_username_from_id(resolved_user_id)

    return {
        "is_live": bool(stream.get("live")),
        "view_count": int(stream.get("viewer_count") or 0),
        "username": username,
        "url": f"https://www.twitch.tv/{username}" if username else None,
    }
