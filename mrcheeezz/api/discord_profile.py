import requests


def build_discord_avatar_url(user):
    user_id = user.get("id")
    avatar_hash = user.get("avatar")

    if not user_id or not avatar_hash:
        return None

    ext = "gif" if avatar_hash.startswith("a_") else "png"
    return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size=512"


def fetch_discord_avatar_url(access_token):
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://discord.com/api/users/@me", headers=headers, timeout=5)

    if response.status_code != 200:
        return None

    return build_discord_avatar_url(response.json())
