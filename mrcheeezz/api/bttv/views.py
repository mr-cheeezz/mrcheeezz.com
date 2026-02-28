from django.http import JsonResponse
import requests


def emote(request, code):
    url = "https://api.betterttv.net/3/emotes/shared/search"
    params = {"query": code, "offset": 0, "limit": 1}

    try:
        response = requests.get(url, params=params, timeout=8)
    except requests.RequestException:
        return JsonResponse({"ok": False, "message": "BTTV API request failed"}, status=502)

    if response.status_code != 200:
        return JsonResponse({"ok": False, "message": "BTTV API error", "status_code": response.status_code}, status=502)

    results = response.json()
    if not results:
        return JsonResponse({"ok": False, "message": "Emote not found"}, status=404)

    emote_data = results[0]
    emote_id = emote_data.get("id")
    return JsonResponse(
        {
            "ok": True,
            "provider": "bttv",
            "id": emote_id,
            "code": emote_data.get("code"),
            "image_type": emote_data.get("imageType"),
            "url_1x": f"https://cdn.betterttv.net/emote/{emote_id}/1x" if emote_id else None,
            "url_2x": f"https://cdn.betterttv.net/emote/{emote_id}/2x" if emote_id else None,
            "url_3x": f"https://cdn.betterttv.net/emote/{emote_id}/3x" if emote_id else None,
        }
    )
