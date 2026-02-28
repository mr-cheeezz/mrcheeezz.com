import time
import requests
import re
from types import TracebackType
from django.http import HttpResponse
from django.utils import timezone
from api.models import SpotifyUser, APICredential
from . import requests as spotify
from .requests import refresh_token, refresh_credential_token
from mrcheeezz import env

from urllib.parse import unquote_plus
from django.http import JsonResponse

from django.http import HttpResponse

offensive_words = ['fuck', 'niggas', 'nigger', 'nigga', 'bitch', 'fucker', 'fucking']


def _get_owner_spotify_access_token():
  # Preferred credential used by website now-playing widget.
  credential = APICredential.objects.filter(provider="spotify_owner").first()
  if credential and credential.access_token:
    if credential.token_expiry and timezone.now() >= credential.token_expiry:
      try:
        return refresh_credential_token(credential, provider="spotify_owner")
      except Exception:
        pass
    return credential.access_token

  # Backward compatibility: allow generic spotify provider credential too.
  generic = APICredential.objects.filter(provider="spotify").first()
  if generic and generic.access_token:
    if generic.token_expiry and timezone.now() >= generic.token_expiry:
      try:
        return refresh_credential_token(generic, provider="spotify")
      except Exception:
        return None
    return generic.access_token

  return None


def _get_user_spotify_access_token(user):
  if user.token_expiry and timezone.now() >= user.token_expiry:
    return refresh_token(user)
  return user.access_token


def _build_now_playing_response(access_token):
  headers = {"Authorization": f"Bearer {access_token}"}
  response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers, timeout=8)

  if response.status_code == 204:
    return JsonResponse({"state": "idle", "message": "Nothing is currently playing"})

  if response.status_code != 200:
    return JsonResponse(
      {"state": "error", "message": "Unable to fetch Spotify playback"},
      status=response.status_code
    )

  data = response.json()
  item = data.get("item")
  if not item:
    return JsonResponse({"state": "idle", "message": "Nothing is currently playing"})

  artists = ", ".join([artist.get("name", "") for artist in item.get("artists", []) if artist.get("name")])
  images = item.get("album", {}).get("images", [])
  cover = ""
  if images:
    cover = images[1].get("url") if len(images) > 1 else images[0].get("url", "")

  return JsonResponse({
    "state": "playing" if data.get("is_playing") else "paused",
    "track": item.get("name", "Unknown Track"),
    "artist": artists or "Unknown Artist",
    "album": item.get("album", {}).get("name", ""),
    "cover_url": cover,
    "track_url": item.get("external_urls", {}).get("spotify", ""),
    "duration_ms": item.get("duration_ms") or 0,
    "progress_ms": data.get("progress_ms") or 0,
    "is_playing": bool(data.get("is_playing")),
    "explicit": bool(item.get("explicit")),
  })

def filter_word(word):
  if len(word) > 2:
    first_letter = word[0]
    last_letter = word[-1]
    middle_letters = '*' * (len(word) - 2)
    return first_letter + middle_letters + last_letter
  else:
    return word

def filter_offensive(text):
  words = text.split()
  for i, word in enumerate(words):
    for bad_word in offensive_words:
      pattern = re.compile(rf'\b{re.escape(bad_word)}\b', re.IGNORECASE)
      if pattern.search(word):
        words[i] = pattern.sub(filter_word(word), word)
  return ' '.join(words)


def top_tracks(request, user_id):
  try:
    user = SpotifyUser.objects.get(user_id=user_id)
  except SpotifyUser.DoesNotExist:
    return HttpResponse("User not found", status=404, content_type='text/plain')

  if timezone.now() >= user.token_expiry:
    try:
      access_token = refresh_token(user)
    except Exception as e:
      return HttpResponse(f"Error refreshing token: {str(e)}", status=500, content_type='text/plain')
  else:
    access_token = user.access_token

  try:
    limit = int(request.GET.get('limit', 5))
    if limit < 1 or limit > 50:
      err = 'more than 50' if limit > 50 else 'less than 1'
      return HttpResponse(f'limit cannot be {err}', status=500, content_type='text/plain')
  except ValueError:
    limit = 5

  try:
    time_range = str(request.GET.get('time_range', 'medium'))

    if time_range == 'short':
      r = 'short_term'
    elif time_range == 'medium':
      r = 'medium_term'
    elif time_range == 'long':
      r = 'long_term'

    if time_range not in ['short', 'medium', 'long']:
      return HttpResponse(f'time_range must be short, medium, or long', status=500, content_type='text/plain')
  except ValueError:
    r = 'medium_term'

  tracks_info = spotify.get_user_top_tracks(access_token, limit, r)

  is_bot = request.GET.get('bot', 'false').lower() == 'true'

  songs_artists_list = []
  for idx, track in enumerate(tracks_info.get('items', []), 1):
    track_name = track.get('name')
    track_name_filterd = filter_offensive(track_name) 
    artists = ', '.join([artist['name'] for artist in track.get('artists', [])])

    suffix = ', ' if is_bot and idx < len(tracks_info.get('items', [])) else ''
    
    songs_artists_list.append(f"{idx}. {track_name_filterd} - {artists}{suffix}")

  response_content = '\n'.join(songs_artists_list)
  
  return HttpResponse(response_content, content_type='text/plain')


def now_playing(request, user_id):
  try:
    user = SpotifyUser.objects.get(user_id=user_id)
  except SpotifyUser.DoesNotExist:
    return HttpResponse("User not found", status=404, content_type='text/plain')

  if timezone.now() >= user.token_expiry:
    access_token = refresh_token(user)
  else:
    access_token = user.access_token

  track_name, artist_name, status_code = spotify.get_currently_playing(access_token)

  if not isinstance(status_code, int):
    status_code = 500

  if status_code == 204:
    return HttpResponse("No song is currently being played", content_type='text/plain')

  if status_code != 200:
    return HttpResponse(
      f"Error {status_code}: Unable to fetch currently playing song",
      status=status_code,
      content_type='text/plain'
    )

  playback_status = spotify.get_playback_status(access_token)
  if playback_status is None:
    return HttpResponse(
      f"Error {status_code}: Unable to fetch playback status",
      status=status_code,
      content_type='text/plain'
    )

  if playback_status == False:
    return HttpResponse("Song is currently paused", content_type='text/plain')

  if not track_name and not artist_name:
    return HttpResponse("No song is currently playing", status=404, content_type='text/plain')

  # --- formatting / filtering ---
  track_name_filtered = filter_offensive(track_name)
  base_song = f"{artist_name} - {track_name_filtered}"

  # --- query params ---
  is_bot = request.GET.get('bot', 'false').lower() == 'true'
  streamer = str(request.GET.get('streamer', '')).strip()
  emote = str(request.GET.get('emote', '')).strip()

  # --- explicit + progress (applies to both formats) ---
  extra_bits = ""

  if request.GET.get('explicit') and spotify.is_explicit(access_token):
    extra_bits += "(E)"

  if request.GET.get('song-progress'):
    progress = spotify.get_song_progress(access_token)
    if progress:
      extra_bits += f" [{progress}]"

  # --- bot output ---
  if is_bot and streamer:
    # If emote is provided: "<streamer> is currently listening to <emote> <song> <emote>"
    # If no emote: "<streamer> is currently listening to <song>"
    if emote:
      response_text = f"{streamer} is currently listening to {emote} {base_song}{extra_bits} {emote}"
    else:
      response_text = f"{streamer} is currently listening to {base_song}{extra_bits}"
    return HttpResponse(response_text, content_type='text/plain')

  # --- default output (your original style) ---
  response_text = f"{base_song}{extra_bits}"
  return HttpResponse(response_text, content_type='text/plain')


def now_playing_card(request, user_id):
  try:
    user = SpotifyUser.objects.get(user_id=user_id)
  except SpotifyUser.DoesNotExist:
    return JsonResponse({"state": "error", "message": "User not found"}, status=404)

  access_token = _get_user_spotify_access_token(user)
  return _build_now_playing_response(access_token)


def now_playing_owner_card(request):
  access_token = _get_owner_spotify_access_token()
  if not access_token:
    # Legacy fallback for setups still using a NowPlayingID-backed SpotifyUser.
    if env.NowPlayingID:
      try:
        legacy_user = SpotifyUser.objects.get(user_id=env.NowPlayingID)
        access_token = _get_user_spotify_access_token(legacy_user)
      except SpotifyUser.DoesNotExist:
        access_token = None

  if not access_token:
    return JsonResponse(
      {
        "state": "error",
        "message": "Owner Spotify is not linked",
        "connect_url": "/spotify/connect/",
      },
      status=503,
    )

  return _build_now_playing_response(access_token)



def song_info(request, user_id):
    try:
      user = SpotifyUser.objects.get(user_id=user_id)
    except SpotifyUser.DoesNotExist:
      return HttpResponse("User not found", status=404, content_type='text/plain')

    if timezone.now() >= user.token_expiry:
      access_token = refresh_token(user)
    else:
      access_token = user.access_token

    song_id, status_code = spotify.get_song_id(access_token)
    if status_code != 200:
        return HttpResponse(f"Error {status_code}: Unable to fetch currently playing song ID.", 
                            status=status_code, content_type='text/plain')

    track_info, status_code = spotify.fetch_track_info(access_token, song_id)
    if status_code != 200:
        return HttpResponse(f"Error {status_code}: Unable to fetch track information.", 
                            status=status_code, content_type='text/plain')

    album_id = track_info['album']['id']
    album_info, status_code = spotify.fetch_album_info(access_token, album_id)
    if status_code != 200:
        return HttpResponse(f"Error {status_code}: Unable to fetch album information.", 
                            status=status_code, content_type='text/plain')

    artist_names = ', '.join([artist['name'] for artist in track_info['artists']])

    if request.GET.get('line', 'false').lower() == 'true':
        response_text = (f"The song {filter_offensive(track_info['name'])} is a part of the album {album_info['name']} by {artist_names}, "
                         f"which has {album_info['total_tracks']} songs in it, released in {album_info['release_date'].split('-')[0]}.")

    else:
        info_keys = ["name", "artists", "album", "release_date", "total_tracks"]
        formatted_info = {
            "name": filter_offensive(track_info['name']),
            "artists": artist_names,
            "album": album_info['name'],
            "release_date": album_info['release_date'].split('-')[0],
            "total_tracks": album_info['total_tracks']
        }
        response_text = '\n'.join([f"{key.capitalize()}: {formatted_info[key]}" for key in info_keys])

    return HttpResponse(response_text, content_type='text/plain')


def last_song(request, user_id):
  try:
    user = SpotifyUser.objects.get(user_id=user_id)
  except SpotifyUser.DoesNotExist:
    return HttpResponse("User not found", status=404, content_type='text/plain')

  if timezone.now() >= user.token_expiry:
    access_token = refresh_token(user)
  else:
    access_token = user.access_token

  track_name, artists, debug_info = spotify.get_most_recently_played(access_token)

  track_name_filterd = filter_offensive(track_name)

  if debug_info:
    return HttpResponse(debug_info, content_type='text/plain')

  if not track_name or not artists:
    return HttpResponse("No recently played song found.", content_type='text/plain')

  response_text = f"{track_name_filterd} - {artists}"

  return HttpResponse(response_text, content_type='text/plain')


def player_queue(request, user_id):
  try:
    user = SpotifyUser.objects.get(user_id=user_id)
  except SpotifyUser.DoesNotExist:
    return HttpResponse("User not found", status=404, content_type='text/plain')

  if timezone.now() >= user.token_expiry:
    access_token = refresh_token(user)
  else:
    access_token = user.access_token

  limit = request.GET.get('limit', 5)
  try:
    limit = int(limit)
  except ValueError:
    return HttpResponse("Invalid limit value", status=400, content_type='text/plain')

  tracks_list, status_code = spotify.get_player_queue(access_token)

  if status_code != 200 or not tracks_list:
    return HttpResponse(
      f"Error {status_code}: Unable to fetch player queue.",
      status=status_code,
      content_type='text/plain'
    )

  tracks_list = tracks_list[:limit]

  is_bot = request.GET.get('bot', 'false').lower() == 'true'

  songs_artists_list = []
  for idx, track in enumerate(tracks_list, 1):
    suffix = ', ' if is_bot and idx < len(tracks_list) else ''
    songs_artists_list.append(f"{idx}. {track}{suffix}")

  response_content = '\n'.join(songs_artists_list)

  return HttpResponse(response_content, content_type='text/plain')

def queue_song(request, user_id):
  EMERGENCY_KEY = "*f8um8123md8()"
  key = (request.GET.get("key") or "").strip()

  if key != EMERGENCY_KEY:
    return HttpResponse("Unauthorized", status=401, content_type="text/plain")


  try:
    user = SpotifyUser.objects.get(user_id=user_id)
  except SpotifyUser.DoesNotExist:
    return HttpResponse("User not found", status=404, content_type='text/plain')

  if timezone.now() >= user.token_expiry:
    try:
      access_token = refresh_token(user)
    except Exception as e:
      return HttpResponse(f"Error refreshing token: {str(e)}", status=500, content_type='text/plain')
  else:
    access_token = user.access_token

  raw = unquote_plus(str(request.GET.get('song_id', '')).strip())
  if not raw:
    return HttpResponse("No song_id provided", status=400, content_type='text/plain')

  track_id = None
  song_label = None

  match = re.search(r"spotify:track:([A-Za-z0-9]{22})", raw)
  if match:
    track_id = match.group(1)

  if not track_id:
    match = re.search(r"open\.spotify\.com/track/([A-Za-z0-9]{22})", raw)
    if match:
      track_id = match.group(1)

  if not track_id and re.fullmatch(r"[A-Za-z0-9]{22}", raw):
    track_id = raw

  if not track_id:
    track_id, song_label, status_code = spotify.search_track(access_token, raw, limit=1)
    if status_code == 404 or not track_id:
      return HttpResponse("No results found for that song", status=404, content_type='text/plain')
    if status_code != 200:
      return HttpResponse(f"Error {status_code}: Unable to search songs", content_type='text/plain')
  else:
    song_label, info_status = spotify.get_track_label(access_token, track_id)
    if info_status != 200 or not song_label:
      return HttpResponse("Unable to fetch song info", status=500, content_type='text/plain')

  song_label = filter_offensive(song_label)

  # Queue the exact track
  success, status_code = spotify.add_to_queue(access_token, track_id)

  if success:
    return HttpResponse(f"Successfully added {song_label} to the queue", content_type='text/plain')

  if status_code == 404:
    return HttpResponse("No active Spotify device. Open Spotify and start playback.", content_type='text/plain')

  if status_code == 403:
    return HttpResponse("Missing permission: user-modify-playback-state (reconnect Spotify).", content_type='text/plain')

  return HttpResponse(f"Error {status_code}: Unable to add song to queue", content_type='text/plain')

def skip_current_song(request, user_id):
  try:
    user = SpotifyUser.objects.get(user_id=user_id)
  except SpotifyUser.DoesNotExist:
    return HttpResponse("User not found", status=404, content_type='text/plain')

  if timezone.now() >= user.token_expiry:
    try:
      access_token = refresh_token(user)
    except Exception as e:
      return HttpResponse(f"Error refreshing token: {str(e)}", status=500, content_type='text/plain')
  else:
    access_token = user.access_token

  success, status_code = spotify.skip_song(access_token)

  if success:
    return HttpResponse("Skipped current song", content_type='text/plain')

  if status_code == 404:
    return HttpResponse("No active Spotify device. Open Spotify and start playback.", content_type='text/plain')

  if status_code == 403:
    return HttpResponse("Missing permission: user-modify-playback-state (reconnect Spotify).", content_type='text/plain')

  return HttpResponse(f"Error {status_code}: Unable to skip song", content_type='text/plain')
