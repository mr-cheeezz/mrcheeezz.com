from .functions import milliseconds_to_minutes_seconds
from mrcheeezz import env
from django.utils import timezone
from api.credentials import get_provider_client_id, get_provider_client_secret
import requests
import datetime

BASE_URL = "https://api.spotify.com/v1/"
CLIENT_ID = env.spotify_client_id
CLIENT_SECRET = env.spotify_client_secret
REDIRECT_URI = env.spotify_redirect_uri

def fetch_spotify_data(access_token, endpoint, params={}):
  headers = {'Authorization': f"Bearer {access_token}"}
  response = requests.get(BASE_URL + endpoint, headers=headers, params=params)
  if response.status_code == 200:
    return response.json()
  return None

def get_spotify_display_name(access_token):
  data = fetch_spotify_data(access_token, "me")
  return data.get("display_name") if data else None

def get_user_top_tracks(access_token, limit=5):
  data = fetch_spotify_data(access_token, "me/top/tracks", {'limit': limit})
  if not data:
    return []

  tracks = data.get('items', [])
  track_info_list = []
  for track in tracks:
    track_name = track.get('name')
    artist_name = track.get('artists', [{}])[0].get('name')
    track_info_list.append({'track_name': track_name, 'artist_name': artist_name})

  return track_info_list

def is_explicit(access_token):
  data = fetch_spotify_data(access_token, "me/player/currently-playing")
  return data and data.get('item', {}).get('explicit', False)

def get_playback_status(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get("https://api.spotify.com/v1/me/player", headers=headers)
    data = response.json()

    if response.status_code != 200:
        return None

    is_playing = data.get('is_playing')
    return is_playing

def get_song_progress(access_token):
  data = fetch_spotify_data(access_token, "me/player/currently-playing")
  if not data:
    return None

  track = data.get('item', {})
  duration = milliseconds_to_minutes_seconds(track.get('duration_ms', 0))
  current_position = milliseconds_to_minutes_seconds(data.get('progress_ms', 0))
  return f"{current_position}/{duration}"

def get_currently_playing(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(BASE_URL + "me/player/currently-playing", headers=headers)

    if response.status_code == 200:
        data = response.json()
        track_name = data.get('item', {}).get('name', "Unknown Track")
        artist_name = data.get('item', {}).get('artists', [{}])[0].get('name', "Unknown Artist")
        return track_name, artist_name, response.status_code
    else:
        return None, None, response.status_code
    
def get_player_queue(access_token, limit=5):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    params = {
        "limit": limit
    }

    response = requests.get("https://api.spotify.com/v1/me/player/queue", headers=headers, params=params)
    
    if response.status_code != 200:
        return None, response.status_code

    tracks_data = response.json()
    
    tracks_list = []
    for track in tracks_data.get('queue', []):
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        tracks_list.append(f"{artist_name} - {track_name}")

    return tracks_list, 200
    
def get_most_recently_played(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=1", headers=headers)

    if response.status_code != 200:
        return None, None, f"API returned {response.status_code}: {response.text}"

    data = response.json()

    if not data.get('items'):
        return None, None, "No items in the returned data."

    recent_track = data['items'][0]['track']
    track_name = recent_track['name']
    artists = ", ".join([artist['name'] for artist in recent_track['artists']])

    return track_name, artists, None

    
def get_artist_info(access_token, artist_id):
  headers = {"Authorization": f"Bearer {access_token}"}
  response = requests.get(BASE_URL + f"artists/{artist_id}", headers=headers)

  if response.status_code == 200:
    data = response.json()
    artist_name = data.get('name', "Unknown Artist")
    artist_genres = data.get('genres', [])
    artist_followers = data.get('followers', {}).get('total', 0)
    return artist_name, artist_genres, artist_followers
  else:
    return None, None, None


def refresh_token(user):
  refresh_data = {
    'grant_type': 'refresh_token',
    'refresh_token': user.refresh_token,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
  }

  response = requests.post('https://accounts.spotify.com/api/token', data=refresh_data)
  response_data = response.json()

  if 'error' in response_data:
    raise Exception(f"Error refreshing token: {response_data['error_description']}")

  user.access_token = response_data.get('access_token')
  user.token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=response_data.get('expires_in'))
  user.save()
  return user.access_token


def refresh_credential_token(credential, provider="spotify_owner"):
  if not credential or not credential.refresh_token:
    raise Exception("Missing refresh token")

  client_id = get_provider_client_id(provider, fallback=CLIENT_ID)
  client_secret = get_provider_client_secret(provider, fallback=CLIENT_SECRET)
  if not client_id or not client_secret:
    raise Exception("Missing Spotify client credentials")

  refresh_data = {
    'grant_type': 'refresh_token',
    'refresh_token': credential.refresh_token,
    'client_id': client_id,
    'client_secret': client_secret,
  }

  response = requests.post('https://accounts.spotify.com/api/token', data=refresh_data, timeout=10)
  response_data = response.json()

  if 'error' in response_data:
    raise Exception(f"Error refreshing token: {response_data.get('error_description', response_data['error'])}")

  credential.access_token = response_data.get('access_token', credential.access_token)
  new_refresh = response_data.get('refresh_token')
  if new_refresh:
    credential.refresh_token = new_refresh
  expires_in = int(response_data.get('expires_in', 3600))
  credential.token_expiry = timezone.now() + datetime.timedelta(seconds=expires_in)
  credential.save(update_fields=["access_token", "refresh_token", "token_expiry", "updated_at"])
  return credential.access_token

def get_user_top_tracks(access_token, limit, time_range):
  return fetch_spotify_data(access_token, "me/top/tracks", {'limit': limit, 'time_range': time_range})

def fetch_track_info(access_token, track_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)
    if response.status_code == 200:
        return response.json(), response.status_code
    else:
        return None, response.status_code
    
def fetch_album_info(access_token, album_id):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.spotify.com/v1/albums/{album_id}", headers=headers)
    if response.status_code == 200:
        return response.json(), response.status_code
    else:
        return None, response.status_code
    
def get_track_label(access_token, track_id):
    track_info, status_code = fetch_track_info(access_token, track_id)

    if status_code != 200 or not track_info:
        return None, status_code

    track_name = track_info.get('name', 'Unknown Song')
    artist_names = ', '.join([artist['name'] for artist in track_info.get('artists', [])]) or 'Unknown Artist'

    return f"{artist_names} - {track_name}", 200

def add_to_queue(access_token, track_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"uri": f"spotify:track:{track_id}"}

    response = requests.post("https://api.spotify.com/v1/me/player/queue", headers=headers, params=params)

    if response.status_code in [200, 204]:
        return True, response.status_code

    return False, response.status_code

def skip_song(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post("https://api.spotify.com/v1/me/player/next", headers=headers)

    if response.status_code in [200, 204]:
        return True, response.status_code

    return False, response.status_code

def search_track(access_token, query, limit=1):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": query,
        "type": "track",
        "limit": limit
    }

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)

    if response.status_code != 200:
        return None, None, response.status_code

    data = response.json()
    items = data.get("tracks", {}).get("items", [])
    if not items:
        return None, None, 404

    track = items[0]
    track_id = track.get("id")
    track_name = track.get("name", "Unknown Song")
    artists = ", ".join([a["name"] for a in track.get("artists", [])]) or "Unknown Artist"

    # label = Artist - Song (same format as your other output)
    label = f"{artists} - {track_name}"

    return track_id, label, 200
