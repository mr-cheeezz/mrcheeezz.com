from django.http import JsonResponse
import requests


def _format_emote(emote_data):
    host = (emote_data.get("host") or {})
    files = host.get("files") or []
    best = files[-1] if files else {}
    cdn_url = None
    if host.get("url") and best.get("name"):
        cdn_url = f"https:{host['url']}/{best['name']}"

    return {
        "ok": True,
        "provider": "7tv",
        "id": emote_data.get("id"),
        "name": emote_data.get("name"),
        "animated": bool(emote_data.get("animated")),
        "url": cdn_url,
    }


def emote(request, name):
    try:
        response = requests.get("https://7tv.io/v3/emote-sets/global", timeout=10)
    except requests.RequestException:
        return JsonResponse({"ok": False, "message": "7TV API request failed"}, status=502)

    if response.status_code != 200:
        return JsonResponse({"ok": False, "message": "7TV API error", "status_code": response.status_code}, status=502)

    emotes = response.json().get("emotes", [])
    for emote_data in emotes:
        if emote_data.get("name", "").lower() == name.lower():
            return JsonResponse(_format_emote(emote_data))

    return JsonResponse({"ok": False, "message": "Emote not found"}, status=404)


def emote_by_id(request, emote_id):
    try:
        response = requests.get(f"https://7tv.io/v3/emotes/{emote_id}", timeout=8)
    except requests.RequestException:
        return JsonResponse({"ok": False, "message": "7TV API request failed"}, status=502)

    if response.status_code != 200:
        return JsonResponse({"ok": False, "message": "7TV API error", "status_code": response.status_code}, status=502)

    return JsonResponse(_format_emote(response.json()))
