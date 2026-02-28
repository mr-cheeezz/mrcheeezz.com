from django.http import JsonResponse
from mrcheeezz import env
from api.credentials import get_provider_config
import requests


def _steam_summary(steam_id):
    api_key = get_provider_config("steam", "api_key", fallback=env.steam_api_key)
    if not api_key:
        return None, JsonResponse({"ok": False, "message": "Steam API key is not configured"}, status=503)

    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": api_key, "steamids": steam_id}

    try:
        response = requests.get(url, params=params, timeout=8)
    except requests.RequestException:
        return None, JsonResponse({"ok": False, "message": "Steam API request failed"}, status=502)

    if response.status_code != 200:
        return None, JsonResponse({"ok": False, "message": "Steam API error", "status_code": response.status_code}, status=502)

    players = response.json().get("response", {}).get("players", [])
    if not players:
        return None, JsonResponse({"ok": False, "message": "Steam user not found"}, status=404)

    return players[0], None


def player_summary(request, steam_id):
    player, error_response = _steam_summary(steam_id)
    if error_response is not None:
        return error_response

    return JsonResponse(
        {
            "ok": True,
            "steam_id": steam_id,
            "personaname": player.get("personaname"),
            "profileurl": player.get("profileurl"),
            "avatarfull": player.get("avatarfull"),
            "personastate": player.get("personastate"),
            "gameextrainfo": player.get("gameextrainfo"),
        }
    )


def current_game(request, steam_id):
    player, error_response = _steam_summary(steam_id)
    if error_response is not None:
        return error_response

    return JsonResponse(
        {
            "ok": True,
            "steam_id": steam_id,
            "game": player.get("gameextrainfo"),
            "ingame": bool(player.get("gameextrainfo")),
        }
    )
