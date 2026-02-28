import requests
from django.utils import timezone
from api.models import SpotifyUser, APICredential
from api.spotify.requests import refresh_token, refresh_credential_token
from mrcheeezz import env


def check_spotify_playing():
    owner_credential = APICredential.objects.filter(provider="spotify_owner").first()
    if owner_credential and owner_credential.access_token:
        if owner_credential.token_expiry and timezone.now() >= owner_credential.token_expiry:
            try:
                access_token = refresh_credential_token(owner_credential, provider="spotify_owner")
            except Exception:
                access_token = None
        else:
            access_token = owner_credential.access_token

        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers, timeout=8)
            if response.status_code == 200:
                payload = response.json()
                return bool(payload.get("is_playing"))

    # Legacy fallback for existing NowPlayingID-based setup.
    try:
        user = SpotifyUser.objects.get(user_id=env.NowPlayingID)
    except SpotifyUser.DoesNotExist:
        return False

    if timezone.now() >= user.token_expiry:
        access_token = refresh_token(user)
    else:
        access_token = user.access_token

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers, timeout=8)

    if response.status_code != 200:
        return False

    payload = response.json()
    return bool(payload.get("is_playing"))


is_playing = check_spotify_playing()
