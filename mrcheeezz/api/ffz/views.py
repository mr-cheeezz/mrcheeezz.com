from django.http import JsonResponse
import requests


def emote(request, code):
    url = "https://api.frankerfacez.com/v1/emoticons"
    params = {"q": code}

    try:
        response = requests.get(url, params=params, timeout=8)
    except requests.RequestException:
        return JsonResponse({"ok": False, "message": "FFZ API request failed"}, status=502)

    if response.status_code != 200:
        return JsonResponse({"ok": False, "message": "FFZ API error", "status_code": response.status_code}, status=502)

    data = response.json()
    sets = data.get("sets", {})
    for emote_set in sets.values():
        for emote_data in emote_set.get("emoticons", []):
            if emote_data.get("name", "").lower() == code.lower():
                urls = emote_data.get("urls", {})
                best_scale = sorted(urls.keys(), key=lambda x: int(x))[-1] if urls else None
                image_path = urls.get(best_scale) if best_scale else None
                image_url = f"https:{image_path}" if image_path and image_path.startswith("//") else image_path
                return JsonResponse(
                    {
                        "ok": True,
                        "provider": "ffz",
                        "id": emote_data.get("id"),
                        "name": emote_data.get("name"),
                        "owner": (emote_data.get("owner") or {}).get("name"),
                        "url": image_url,
                    }
                )

    return JsonResponse({"ok": False, "message": "Emote not found"}, status=404)
