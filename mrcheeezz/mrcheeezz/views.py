from django.shortcuts import render, redirect as dajango_redirect
from django.contrib.auth.views import LogoutView
from django.views import View
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from urllib.parse import urlparse
from django.utils import timezone
from api.models import SpotifyUser, APICredential
from api.spotify.requests import refresh_token, refresh_credential_token
from api.credentials import get_provider_access_token
from api.roblox import requests as roblox_api
from .log import logger
from . import env
import requests
import json
import os
import markdown
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_BASE_DIR = PROJECT_ROOT / "static"
EXCLUDE_DIRS = ['.webassets-cache']

class logout(LogoutView):
    template_name = 'admin/logged_out.html'

class login(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'admin/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            logger.info(f'User {username} logged in.')
            if user.is_superuser or user.is_staff:
                return redirect(request, message='Succsuffly logged in', e_url='/admin')
            else:
                return redirect(request, message='Succsuffly logged in', e_url='/')
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'admin/login.html', context)
        
def redirect(request, message=None, e_url=None):
    url = request.GET.get('url', e_url)

    parsed_url = urlparse(url)
    outside_of_domain = parsed_url.scheme and parsed_url.netloc

    time_to_wait = 1 * 1000

    if outside_of_domain:
        time_to_wait = 2.5 * 1000

    context = {
        'redirect_url': url,
        'message': message,
        'domain': env.url,
        'await': time_to_wait,
        'outside_of_domain': outside_of_domain,
    }

    return render(request, 'redirect.html', context)

def get_tweets(bearer_token=None, username=env.twitter_handle, count=5):
    bearer_token = bearer_token or env.twitter_bearer_token
    if not bearer_token or not username:
        return JsonResponse({'error': 'Twitter API credentials are not configured'}, status=503)

    headers = {
        'Authorization': f'Bearer {bearer_token}',
    }

    params = {
        'screen_name': username,
        'count': count,
    }

    api_url = 'https://api.twitter.com/2/tweets'

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        tweets = response.json()
        return JsonResponse({'tweets': tweets})
    else:
        error_message = f"Failed to fetch tweets. Status code: {response.status_code}"
        logger.info(error_message)
        error_data = response.json()
        logger.info("Twitter API error payload: %s", error_data)
        return JsonResponse({'error': error_message, 'details': error_data})

def get_game_time(request):
    json_file_path = STATIC_BASE_DIR / 'scripts' / 'game_change.json'

    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            last_game_change_time = data.get("last_game_change_time")
            return JsonResponse({"last_game_change_time": last_game_change_time})
    except FileNotFoundError:
        return JsonResponse({"last_game_change_time": None})
    
def reset_game_time(request):
    json_file_path = STATIC_BASE_DIR / 'scripts' / 'game_change.json'

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump({"last_game_change_time": None}, json_file)

    return JsonResponse({"status": "success"})

def update_game_time(request):
    json_file_path = STATIC_BASE_DIR / 'scripts' / 'game_change.json'

    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {}

    last_game_change_time = int(request.GET.get('last_game_change_time', 0))
    data["last_game_change_time"] = last_game_change_time

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file)

    return JsonResponse({"status": "success"})
        
def fetch_steam_data(request):
    STEAM_API_KEY = env.steam_api_key
    STEAM_USER_ID = env.steam_user_id
    if not STEAM_API_KEY or not STEAM_USER_ID:
        return JsonResponse({'gameextrainfo': False})

    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={STEAM_USER_ID}'
    try:
        response = requests.get(url, timeout=8)
    except requests.RequestException:
        return JsonResponse({'gameextrainfo': False})

    if response.status_code == 200:
        data = response.json()
        if 'response' in data and 'players' in data['response']:
            players = data['response']['players']
            if players:
                player = players[0]
                if 'gameextrainfo' in player:
                    game_name = player['gameextrainfo']
                    return JsonResponse({'gameextrainfo': game_name})
    
    return JsonResponse({'gameextrainfo': False})

def fetch_roblox_data(request):
    credential = APICredential.objects.filter(provider="roblox").first()
    oauth_token = credential.access_token if credential else None
    if not oauth_token:
        return JsonResponse({'gameextrainfo': False})

    linked_user_id = None
    if credential and isinstance(credential.config, dict):
        linked_user_id = credential.config.get("linked_user_id")

    if not linked_user_id:
        try:
            info = requests.get(
                "https://apis.roblox.com/oauth/v1/userinfo",
                headers={"Authorization": f"Bearer {oauth_token}"},
                timeout=8,
            ).json()
            linked_user_id = str(info.get("sub") or "").strip() or None
        except Exception:
            linked_user_id = None

    if not linked_user_id:
        return JsonResponse({'gameextrainfo': False})

    presence_data = roblox_api.get_presence_oauth(linked_user_id, oauth_token)
    if not presence_data:
        return JsonResponse({'gameextrainfo': False})

    location = (presence_data.get("lastLocation") or "").strip()
    status = int(presence_data.get("userPresenceType") or 0)
    if status == 0 or location.lower() == "website" or not location:
        return JsonResponse({'gameextrainfo': False})
    return JsonResponse({'gameextrainfo': location})
    
def fetch_game(request):
    STEAM_API_KEY = env.steam_api_key
    STEAM_USER_ID = env.steam_user_id
    steam_game = None
    steam_profile_url = ""
    steam_game_url = ""
    if STEAM_API_KEY and STEAM_USER_ID:
        steam_url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={STEAM_USER_ID}'
        try:
            steam_response = requests.get(steam_url, timeout=8)
            if steam_response.status_code == 200:
                steam_data = steam_response.json()
                if 'response' in steam_data and 'players' in steam_data['response']:
                    players = steam_data['response']['players']
                    if players:
                        player = players[0]
                        steam_profile_url = (player.get('profileurl') or "").strip()
                        if 'gameextrainfo' in player:
                            steam_game = player['gameextrainfo']
                            game_id = str(player.get("gameid") or "").strip()
                            if game_id.isdigit():
                                steam_game_url = f"https://store.steampowered.com/app/{game_id}/"
        except requests.RequestException:
            steam_game = None
    
    roblox_game = None
    roblox_profile_url = ""
    roblox_game_url = ""
    fallback_user_id = None
    linked_user_id = None

    configured_roblox_user = (env.roblox_user or "").strip()
    if configured_roblox_user:
        if configured_roblox_user.isdigit():
            fallback_user_id = configured_roblox_user
        else:
            try:
                resolved = roblox_api.get_id_from_user(configured_roblox_user)
                resolved_id = str(resolved.get("userId") or "").strip()
                fallback_user_id = resolved_id or None
            except Exception:
                fallback_user_id = None

    credential = APICredential.objects.filter(provider="roblox").first()
    oauth_token = None
    if credential and credential.access_token:
        if credential.token_expiry and timezone.now() >= credential.token_expiry:
            try:
                oauth_token = refresh_credential_token(credential, provider="roblox")
            except Exception:
                oauth_token = None
        else:
            oauth_token = credential.access_token

    if oauth_token:
        if credential and isinstance(credential.config, dict):
            linked_user_id = credential.config.get("linked_user_id")

        if not linked_user_id:
            try:
                info = requests.get(
                    "https://apis.roblox.com/oauth/v1/userinfo",
                    headers={"Authorization": f"Bearer {oauth_token}"},
                    timeout=8,
                ).json()
                linked_user_id = str(info.get("sub") or "").strip() or None
            except Exception:
                linked_user_id = None

        if linked_user_id:
            presence_data = roblox_api.get_presence_oauth(linked_user_id, oauth_token)
            if not presence_data:
                # OAuth token can become invalid; fallback to .ROBLOSECURITY presence.
                try:
                    presence_data = roblox_api.get_presence(int(linked_user_id))
                except Exception:
                    presence_data = None
            if presence_data:
                location = (presence_data.get("lastLocation") or "").strip()
                status = int(presence_data.get("userPresenceType") or 0)
                if status != 0 and location and location.lower() != "website":
                    roblox_game = location
                    place_id = str(presence_data.get("placeId") or "").strip()
                    if place_id.isdigit():
                        roblox_game_url = f"https://www.roblox.com/games/{place_id}"

    # Config fallback: if linked account presence has no active game,
    # allow explicit roblox.user from config.ini (username or numeric id).
    if not roblox_game and fallback_user_id:
        try:
            fallback_presence = roblox_api.get_presence(int(fallback_user_id))
        except Exception:
            fallback_presence = None
        if fallback_presence:
            location = (fallback_presence.get("lastLocation") or "").strip()
            status = int(fallback_presence.get("userPresenceType") or 0)
            if status != 0 and location and location.lower() != "website":
                roblox_game = location
                place_id = str(fallback_presence.get("placeId") or "").strip()
                if place_id.isdigit():
                    roblox_game_url = f"https://www.roblox.com/games/{place_id}"

    if linked_user_id and str(linked_user_id).isdigit():
        roblox_profile_url = f"https://www.roblox.com/users/{linked_user_id}/profile"
    elif fallback_user_id and str(fallback_user_id).isdigit():
        roblox_profile_url = f"https://www.roblox.com/users/{fallback_user_id}/profile"

    active_platform = ""
    active_game = ""
    active_profile_url = ""
    active_game_url = ""
    if steam_game:
        active_platform = "steam"
        active_game = steam_game
        active_profile_url = steam_profile_url
        active_game_url = steam_game_url
    elif roblox_game:
        active_platform = "roblox"
        active_game = roblox_game
        active_profile_url = roblox_profile_url
        active_game_url = roblox_game_url

    return JsonResponse(
        {
            'steam': steam_game,
            'roblox': roblox_game,
            'steam_profile_url': steam_profile_url,
            'steam_game_url': steam_game_url,
            'roblox_profile_url': roblox_profile_url,
            'roblox_game_url': roblox_game_url,
            'platform': active_platform,
            'game': active_game,
            'profile_url': active_profile_url,
            'game_url': active_game_url,
        }
    )

def check_spotify_playing(request):
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
                return JsonResponse({'is_playing': bool(payload.get('is_playing'))})

    # Legacy fallback for existing NowPlayingID-based setup.
    try:
        user = SpotifyUser.objects.get(user_id=env.NowPlayingID)
    except SpotifyUser.DoesNotExist:
        return JsonResponse({'is_playing': False})

    if timezone.now() >= user.token_expiry:
        access_token = refresh_token(user)
    else:
        access_token = user.access_token

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers, timeout=8)

    if response.status_code != 200:
        return JsonResponse({'is_playing': False})

    payload = response.json()
    return JsonResponse({'is_playing': bool(payload.get('is_playing'))})
    


class ErrorMessageHandler:
    def __init__(self, requested_url, error_code, admin_page, project, bot, blog, static, media):
        self.requested_url = requested_url
        self.error_code = error_code
        self.admin_page = admin_page
        self.project = project
        self.bot = bot
        self.blog = blog
        self.static = static
        self.media = media
        self.error_messages = {
            '400': 'Bad Request',
            '401': 'Unauthorized Access',
            '403': 'Forbidden',
            '404': 'Page Not Found',
            '500': 'Internal Server Error',
            '502': 'Bad Gateway',
        }

    def get_extra_message(self):
        if self.admin_page and self.error_code in ['401', '403']:
            return f"You don't have access to {self.request.path}."

        elif self.error_code == 404:
            if self.project or self.bot or self.blog:
                entity_type = 'project' if self.project else 'bot' if self.bot else 'post'
                entity_code = self.requested_url[10:] if self.project else self.requested_url[6:] 
                return f"The {entity_type} `{entity_code}` does not exist."
            else:
                if self.requested_url == '/error/404.html':
                    return "This is an error on nginx."
                else:
                    entity_type = 'file' if self.static else 'image' if self.media else 'page'
                    entity_code = self.requested_url[1:]
                    return f"The {entity_type} `{entity_code}` can't be found."

        return ""

    def get_main_message(self):
        if self.project and self.error_code == 404:
            return "Project Not Found"
        elif self.bot and self.error_code == 404:
            return "Bot Not Found"
        elif self.blog and self.error_code == 404:
            return "Post Not Found"
        else:
            return self.error_messages.get(str(self.error_code), 'Unknown Error')

    
class ErrorHandler:
    def __init__(self, request, exception=None, error_code=None):
        self.request = request
        self.exception = exception
        self.error_code = error_code
        self.error_messages = {
            '400': 'Bad Request',
            '401': 'Unauthorized Access',
            '403': 'Forbidden',
            '404': 'Page Not Found',
            '500': 'Internal Server Error',
            '502': 'Bad Gateway',
        }

    def get_error_message(self):
        if self.error_code is None:
            self.error_code = 400

        error_message = self.error_messages.get(str(self.error_code), 'Unknown Error')
        requested_url = self.request.path

        excluded_urls = ['/api/spotify/is-playing', '/api/steam/game']

        static = 'static' in requested_url
        media = 'media' in requested_url
        is_project = 'project' in requested_url
        is_bot = 'bots' in requested_url
        is_blog = 'blog' in requested_url
        admin_page = 'admin' in requested_url

        if requested_url not in excluded_urls:
            logger.info(f'User encountered error {self.error_code} {error_message} on {requested_url}.')

        error_handler = ErrorMessageHandler(
            requested_url, self.error_code, admin_page, is_project, is_bot, is_blog, static, media
        )

        extra_message = error_handler.get_extra_message()
        if extra_message:
            extra_message = markdown.markdown(extra_message)

        main_message = error_handler.get_main_message()
        if main_message:
            main_message = main_message

        context = {
            'error_code': self.error_code,
            'error_message': main_message,
            'requested_url': requested_url,

            'more': False,
            'error': True,

            'static': static,
            'media': media,
            'project': is_project,
            'bot': is_bot,
            'blog': is_blog,

            'admin_page': admin_page,
            
            'extra_message': extra_message, 
        }

        return context

    def render_error_page(self, template_name='error.html'):
        context = self.get_error_message()
        return render(self.request, template_name, context)

def error_400(request, exception=None):
    error_handler = ErrorHandler(request, exception, 400)
    return error_handler.render_error_page()

def error_401(request, exception=None):
    error_handler = ErrorHandler(request, exception, 401)
    return error_handler.render_error_page()

def error_403(request, exception=None):
    error_handler = ErrorHandler(request, exception, 403)
    return error_handler.render_error_page()

def error_404(request, exception=None):
    error_handler = ErrorHandler(request, exception, 404)
    return error_handler.render_error_page()

def error_500(request, exception=None):
    error_handler = ErrorHandler(request, exception, 500)
    return error_handler.render_error_page()

def error_502(request, exception=None):
    error_handler = ErrorHandler(request, exception, 502)
    return error_handler.render_error_page()
