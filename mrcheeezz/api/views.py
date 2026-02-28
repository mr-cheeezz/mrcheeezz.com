from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse, URLPattern, URLResolver, get_resolver
from django.contrib.auth.decorators import user_passes_test
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import SpotifyUser, APICredential
from .credentials import (
  get_provider_access_token,
  get_provider_client_id,
  get_provider_client_secret,
  get_provider_redirect_uri,
  get_provider_config,
)
from .discord_profile import build_discord_avatar_url
from .spotify import requests as spotify
from .roblox import requests as roblox_requests
from mrcheeezz import env
import datetime
import requests
import random
import string
import re
import markdown
from pathlib import Path
from urllib.parse import urlencode

SCOPES = 'user-top-read user-library-read user-read-currently-playing user-read-playback-state user-read-private user-read-recently-played user-modify-playback-state user-read-playback-position playlist-read-private playlist-read-collaborative'
AUTH_URL = 'https://accounts.spotify.com/authorize'
DISCORD_OAUTH_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
DISCORD_OAUTH_TOKEN_URL = "https://discord.com/api/oauth2/token"
ROBLOX_OAUTH_AUTHORIZE_URL = "https://apis.roblox.com/oauth/v1/authorize"
ROBLOX_OAUTH_TOKEN_URL = "https://apis.roblox.com/oauth/v1/token"

INTERNAL_API_ROUTES = {
  "api",
  "api/schema",
  "api/<path:extra>",
  "api/game",
  "api/steam/game",
  "api/roblox/game",
  "api/spotify/is-playing",
  "api/steam/change-time",
  "api/steam/reset-time",
  "api/steam/get-time",
  "api/spotify/now-playing-card",
  "api/spotify/now-playing-card/<str:user_id>",
  "api/spotify/now-playing/<str:user_id>",
  "api/spotify/owner/now-playing-card",
}

EMOTE_PROVIDER_TAGS = {"7tv", "bttv", "ffz"}
PREFERRED_TAG_ORDER = [
  "roblox",
  "spotify",
  "steam",
  "twitch",
]

QUERY_PARAMETER_MAP = {
  "api/roblox/presence/<str:username>": [
    {
      "name": "show_user",
      "in": "query",
      "required": False,
      "schema": {"type": "boolean"},
      "description": "Include username/display name in response text.",
    },
    {
      "name": "use_display",
      "in": "query",
      "required": False,
      "schema": {"type": "boolean"},
      "description": "When show_user=true, use display name instead of username.",
    },
  ],
}

def api_404(request, extra):
  return HttpResponseNotFound('Endpoint Not Found', content_type='text/plain')

def rate_limit(request, exception):
  return HttpResponse('You are being rate limited', status=429, content_type='text/plain')


def _store_provider_tokens(provider, token_payload):
  credential, _ = APICredential.objects.get_or_create(provider=provider)
  credential.access_token = token_payload.get("access_token", "") or ""
  credential.refresh_token = token_payload.get("refresh_token", "") or ""
  expires_in = token_payload.get("expires_in")
  if expires_in:
    try:
      credential.token_expiry = timezone.now() + datetime.timedelta(seconds=int(expires_in))
    except (TypeError, ValueError):
      credential.token_expiry = None
  else:
    credential.token_expiry = None
  credential.save()
  return credential

def _route_to_openapi_path(route):
  # Convert Django path converters like <str:name> or <int:id> to {name}/{id}.
  return re.sub(r"<(?:[^:>]+:)?([^>]+)>", r"{\1}", route)

def _extract_path_parameters(route):
  converter_to_schema = {
    "int": "integer",
    "slug": "string",
    "uuid": "string",
    "str": "string",
    "path": "string",
  }
  params = []
  for match in re.finditer(r"<(?:(?P<converter>[^:>]+):)?(?P<name>[^>]+)>", route):
    converter = match.group("converter") or "str"
    name = match.group("name")
    schema_type = converter_to_schema.get(converter, "string")
    params.append(
      {
        "name": name,
        "in": "path",
        "required": True,
        "schema": {"type": schema_type},
      }
    )
  return params


def _iter_urlpatterns(patterns, prefix=""):
  for pattern in patterns:
    route = str(pattern.pattern)
    full = f"{prefix}{route}"
    if isinstance(pattern, URLResolver):
      yield from _iter_urlpatterns(pattern.url_patterns, full)
    elif isinstance(pattern, URLPattern):
      yield full, pattern


def _guess_methods(callback):
  view_class = getattr(callback, "view_class", None)
  if view_class is None:
    return ["get"]

  methods = []
  for method in ["get", "post", "put", "patch", "delete"]:
    if hasattr(view_class, method):
      methods.append(method)

  return methods or ["get"]


def _tag_from_route(raw_route):
  # /api/spotify/foo -> spotify
  parts = [p for p in raw_route.split("/") if p]
  if len(parts) >= 2:
    return parts[1].lower()
  return "core"


def _normalize_route(raw_route):
  return raw_route.strip("/")


def _route_is_public_api(raw_route):
  normalized = _normalize_route(raw_route)
  return normalized.startswith("api") and normalized not in INTERNAL_API_ROUTES


def _query_parameters_for_route(raw_route):
  return QUERY_PARAMETER_MAP.get(_normalize_route(raw_route), [])


def _sort_tag_key(tag):
  lowered = tag.lower()
  if lowered in PREFERRED_TAG_ORDER:
    return (0, PREFERRED_TAG_ORDER.index(lowered), lowered)
  if lowered in EMOTE_PROVIDER_TAGS:
    return (2, 0, lowered)
  return (1, 0, lowered)


def _summary_from_pattern(pattern, callback):
  if pattern.name:
    return pattern.name.replace("_", " ").replace("-", " ").title()
  return callback.__name__.replace("_", " ").title()


def openapi_schema_view(request):
  paths = {}

  for raw_route, pattern in _iter_urlpatterns(get_resolver().url_patterns):
    if not _route_is_public_api(raw_route):
      continue

    openapi_path = "/" + _route_to_openapi_path(raw_route).lstrip("/")
    callback = pattern.callback
    methods = _guess_methods(callback)
    tag = _tag_from_route(raw_route)
    summary = _summary_from_pattern(pattern, callback)
    path_parameters = _extract_path_parameters(raw_route)
    query_parameters = _query_parameters_for_route(raw_route)
    parameters = path_parameters + query_parameters

    path_item = paths.setdefault(openapi_path, {})
    for method in methods:
      path_item[method] = {
        "tags": [tag],
        "summary": summary,
        "operationId": f"{tag}_{summary.lower().replace(' ', '_')}_{method}",
        "parameters": parameters,
        "responses": {
          "200": {"description": "Success"},
        },
      }

  used_tags = sorted(
    {
      tag
      for path_item in paths.values()
      for operation in path_item.values()
      for tag in operation.get("tags", [])
    },
    key=_sort_tag_key,
  )

  schema = {
    "openapi": "3.0.2",
    "info": {
      "title": "Website API",
      "version": "1.0.0",
      "description": "Swagger/OpenAPI docs for Website API endpoints.",
    },
    "tags": [{"name": tag} for tag in used_tags],
    "paths": dict(sorted(paths.items())),
  }
  return JsonResponse(schema)


class SwaggerDocsView(TemplateView):
  template_name = 'documents/api.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['active_page'] = 'api'
    context['schema_url'] = reverse('api-openapi-schema')
    markdown_path = Path(settings.PROJECT_ROOT) / 'static' / 'markdown' / 'api.md'
    if markdown_path.exists():
      markdown_content = markdown_path.read_text(encoding='utf-8')
      context['api_markdown'] = mark_safe(
        markdown.markdown(markdown_content, extensions=['toc', 'tables', 'abbr', 'fenced_code'])
      )
    else:
      context['api_markdown'] = ""
    return context

def spotify_connect(request):
  # Owner website Spotify linking flow (separate from public API user linking).
  client_id = get_provider_client_id("spotify_owner", fallback=get_provider_client_id("spotify", fallback=env.spotify_client_id))
  redirect_uri = get_provider_redirect_uri("spotify_owner", fallback=get_provider_redirect_uri("spotify", fallback=env.spotify_redirect_uri))
  auth_params = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': SCOPES,
    'show_dialog': 'false',
  }

  url = AUTH_URL + '?' + '&'.join([f"{key}={value}" for key, value in auth_params.items()])

  return HttpResponseRedirect(url)


@user_passes_test(lambda u: u.is_superuser)
def spotify_auth(request):
  return HttpResponseRedirect(reverse('spotify_connect'))


def spotify_api_connect(request):
  # Public/API user Spotify linking flow.
  client_id = get_provider_client_id("spotify", fallback=env.spotify_client_id)
  redirect_uri = get_provider_redirect_uri("spotify", fallback=env.spotify_redirect_uri)
  auth_params = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': SCOPES,
    'show_dialog': 'false',
  }
  url = AUTH_URL + '?' + '&'.join([f"{key}={value}" for key, value in auth_params.items()])
  return HttpResponseRedirect(url)


@user_passes_test(lambda u: u.is_superuser)
def discord_connect(request):
  discord_client_id = get_provider_client_id("discord", fallback=env.discord_client_id)
  discord_redirect_uri = get_provider_redirect_uri("discord", fallback=env.discord_redirect_uri)
  if not (discord_client_id and discord_redirect_uri):
    return JsonResponse({"ok": False, "message": "Discord OAuth client_id/redirect_uri missing in admin credentials (or config.ini fallback)"}, status=400)

  params = {
    "client_id": discord_client_id,
    "response_type": "code",
    "redirect_uri": discord_redirect_uri,
    "scope": "identify",
    "prompt": "consent",
  }
  return HttpResponseRedirect(f"{DISCORD_OAUTH_AUTHORIZE_URL}?{urlencode(params)}")


@user_passes_test(lambda u: u.is_superuser)
def discord_callback(request):
  code = request.GET.get("code")
  if not code:
    return JsonResponse({"ok": False, "message": "No code provided by Discord"}, status=400)

  discord_client_id = get_provider_client_id("discord", fallback=env.discord_client_id)
  discord_client_secret = get_provider_client_secret("discord", fallback=env.discord_client_secret)
  discord_redirect_uri = get_provider_redirect_uri("discord", fallback=env.discord_redirect_uri)
  if not (discord_client_id and discord_client_secret and discord_redirect_uri):
    return JsonResponse({"ok": False, "message": "Discord OAuth config missing in admin credentials (or config.ini fallback)"}, status=400)

  token_data = {
    "client_id": discord_client_id,
    "client_secret": discord_client_secret,
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": discord_redirect_uri,
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  token_response = requests.post(DISCORD_OAUTH_TOKEN_URL, data=token_data, headers=headers, timeout=10)

  if token_response.status_code != 200:
    return JsonResponse(
      {"ok": False, "message": "Discord token exchange failed", "status_code": token_response.status_code},
      status=502,
    )

  payload = token_response.json()
  credential = _store_provider_tokens("discord", payload)
  return JsonResponse({"ok": True, "provider": "discord", "token_saved": bool(credential.access_token)})


@user_passes_test(lambda u: u.is_superuser)
def roblox_connect(request):
  roblox_client_id = get_provider_client_id("roblox", fallback=env.roblox_oauth_client_id)
  roblox_redirect_uri = get_provider_redirect_uri("roblox", fallback=env.roblox_oauth_redirect_uri)
  roblox_oauth_scope = get_provider_config("roblox", "oauth_scope", fallback=env.roblox_oauth_scope or "openid profile")
  if not (roblox_client_id and roblox_redirect_uri):
    return JsonResponse({"ok": False, "message": "Roblox OAuth client_id/redirect_uri missing in admin credentials (or config.ini fallback)"}, status=400)

  params = {
    "client_id": roblox_client_id,
    "response_type": "code",
    "redirect_uri": roblox_redirect_uri,
    "scope": roblox_oauth_scope,
  }
  return HttpResponseRedirect(f"{ROBLOX_OAUTH_AUTHORIZE_URL}?{urlencode(params)}")


@user_passes_test(lambda u: u.is_superuser)
def roblox_callback(request):
  code = request.GET.get("code")
  if not code:
    return JsonResponse({"ok": False, "message": "No code provided by Roblox"}, status=400)

  roblox_client_id = get_provider_client_id("roblox", fallback=env.roblox_oauth_client_id)
  roblox_client_secret = get_provider_client_secret("roblox", fallback=env.roblox_oauth_client_secret)
  roblox_redirect_uri = get_provider_redirect_uri("roblox", fallback=env.roblox_oauth_redirect_uri)
  if not (roblox_client_id and roblox_client_secret and roblox_redirect_uri):
    return JsonResponse({"ok": False, "message": "Roblox OAuth config missing in admin credentials (or config.ini fallback)"}, status=400)

  token_data = {
    "grant_type": "authorization_code",
    "code": code,
    "client_id": roblox_client_id,
    "client_secret": roblox_client_secret,
    "redirect_uri": roblox_redirect_uri,
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  token_response = requests.post(ROBLOX_OAUTH_TOKEN_URL, data=token_data, headers=headers, timeout=10)

  if token_response.status_code != 200:
    return JsonResponse(
      {"ok": False, "message": "Roblox token exchange failed", "status_code": token_response.status_code},
      status=502,
    )

  payload = token_response.json()
  credential = _store_provider_tokens("roblox", payload)

  # Persist linked Roblox account id so owner/game presence does not depend on config.ini user.
  linked_user_id = None
  linked_username = None
  if credential.access_token:
    userinfo_response = requests.get(
      "https://apis.roblox.com/oauth/v1/userinfo",
      headers={"Authorization": f"Bearer {credential.access_token}"},
      timeout=8,
    )
    if userinfo_response.status_code == 200:
      info = userinfo_response.json()
      linked_user_id = str(info.get("sub") or "").strip() or None
      if linked_user_id:
        try:
          user_data = roblox_requests.get_user_data(int(linked_user_id))
          linked_username = user_data.get("username")
        except Exception:
          linked_username = None

  current_config = credential.config if isinstance(credential.config, dict) else {}
  if linked_user_id:
    current_config["linked_user_id"] = linked_user_id
  if linked_username:
    current_config["linked_username"] = linked_username
  credential.config = current_config
  credential.save(update_fields=["config", "updated_at"])

  return JsonResponse(
    {
      "ok": True,
      "provider": "roblox",
      "token_saved": bool(credential.access_token),
      "linked_user_id": linked_user_id,
      "linked_username": linked_username,
    }
  )


@user_passes_test(lambda u: u.is_superuser)
def twitch_auth(request):
  twitch_client_id = get_provider_client_id("twitch", fallback=env.twitch_client_id)
  token = get_provider_access_token("twitch")
  if not token:
    return JsonResponse({"ok": False, "message": "Missing Twitch access token in database"}, status=400)

  headers = {"Authorization": f"OAuth {token}"}
  response = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)

  if response.status_code != 200:
    return JsonResponse(
      {
        "ok": False,
        "message": "Twitch token validation failed",
        "status_code": response.status_code,
      },
      status=response.status_code,
    )

  data = response.json()
  return JsonResponse(
    {
      "ok": True,
      "client_id": data.get("client_id"),
      "login": data.get("login"),
      "user_id": data.get("user_id"),
      "scopes": data.get("scopes", []),
      "expires_in": data.get("expires_in"),
      "configured_client_id": twitch_client_id,
    }
  )


@user_passes_test(lambda u: u.is_superuser)
def roblox_auth(request):
  oauth_token = get_provider_access_token("roblox")
  if oauth_token:
    response = requests.get("https://apis.roblox.com/oauth/v1/userinfo", headers={"Authorization": f"Bearer {oauth_token}"}, timeout=8)
    if response.status_code == 200:
      data = response.json()
      linked_user_id = str(data.get("sub") or "").strip() or None
      credential = APICredential.objects.filter(provider="roblox").first()
      if credential and linked_user_id:
        current_config = credential.config if isinstance(credential.config, dict) else {}
        current_config["linked_user_id"] = linked_user_id
        try:
          user_data = roblox_requests.get_user_data(int(linked_user_id))
          current_config["linked_username"] = user_data.get("username") or current_config.get("linked_username")
        except Exception:
          pass
        credential.config = current_config
        credential.save(update_fields=["config", "updated_at"])

      return JsonResponse(
        {
          "ok": True,
          "message": "Roblox OAuth token is valid",
          "sub": data.get("sub"),
          "linked_user_id": linked_user_id,
        }
      )

  cookie = get_provider_config("roblox", "roblosecurity", fallback=env.roblox_cookie)
  if not cookie:
    return JsonResponse({"ok": False, "message": "Missing Roblox OAuth token and ROBLOSECURITY cookie"}, status=400)

  csrf_token = roblox_requests.get_xcsrf(cookie)
  if not csrf_token:
    return JsonResponse({"ok": False, "message": "Unable to validate Roblox cookie"}, status=401)

  return JsonResponse({"ok": True, "message": "Roblox cookie auth looks valid", "csrf_token_received": True})


@user_passes_test(lambda u: u.is_superuser)
def discord_auth(request):
  token = get_provider_access_token("discord")
  if not token:
    return JsonResponse(
      {
        "ok": False,
        "message": "Missing Discord access token in database",
        "next_step": "Open /discord/connect/ while logged in as superuser to link Discord.",
        "connect_url": "/discord/connect/",
        "admin_credentials_url": "/a/api/apicredential/",
      },
      status=400,
    )

  headers = {"Authorization": f"Bearer {token}"}
  response = requests.get("https://discord.com/api/users/@me", headers=headers, timeout=5)

  if response.status_code != 200:
    return JsonResponse(
      {
        "ok": False,
        "message": "Discord token validation failed",
        "status_code": response.status_code,
        "next_step": "Relink with /discord/connect/ to refresh Discord access token.",
      },
      status=response.status_code,
    )

  data = response.json()
  return JsonResponse(
    {
      "ok": True,
      "id": data.get("id"),
      "username": data.get("username"),
      "global_name": data.get("global_name"),
      "avatar_url": build_discord_avatar_url(data),
    }
  )


def generate_unique_user_id():
    while True:
        uid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        if not SpotifyUser.objects.filter(user_id=uid).exists():
            return uid

def spotify_callback(request):
    # Owner website Spotify callback -> APICredential (spotify_owner).
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Error: No code provided.", status=400)

    client_id = get_provider_client_id("spotify_owner", fallback=get_provider_client_id("spotify", fallback=env.spotify_client_id))
    client_secret = get_provider_client_secret("spotify_owner", fallback=get_provider_client_secret("spotify", fallback=env.spotify_client_secret))
    redirect_uri = get_provider_redirect_uri("spotify_owner", fallback=get_provider_redirect_uri("spotify", fallback=env.spotify_redirect_uri))

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=token_data)
    response_data = response.json()
    
    if 'error' in response_data:
        return HttpResponse(f"Error: {response_data['error_description']}", status=400)

    credential = _store_provider_tokens("spotify_owner", response_data)
    return JsonResponse({"ok": True, "provider": "spotify_owner", "token_saved": bool(credential.access_token)})


def spotify_api_callback(request):
    # Public/API user callback -> SpotifyUser (user_id based API usage).
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Error: No code provided.", status=400)

    client_id = get_provider_client_id("spotify", fallback=env.spotify_client_id)
    client_secret = get_provider_client_secret("spotify", fallback=env.spotify_client_secret)
    redirect_uri = get_provider_redirect_uri("spotify", fallback=env.spotify_redirect_uri)

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post('https://accounts.spotify.com/api/token', data=token_data)
    response_data = response.json()
    
    if 'error' in response_data:
        return HttpResponse(f"Error: {response_data['error_description']}", status=400)

    access_token = response_data.get('access_token')
    refresh_token = response_data.get('refresh_token')
    expires_in = response_data.get('expires_in')

    spotify_user_resp = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=10,
    )
    if spotify_user_resp.status_code != 200:
        return HttpResponse("Error: Unable to fetch Spotify profile.", status=spotify_user_resp.status_code)
    spotify_user_data = spotify_user_resp.json()
    spotify_id = spotify_user_data.get('id')
    if not spotify_id:
        return HttpResponse("Error: Spotify profile missing id.", status=500)

    try:
        existing_user = SpotifyUser.objects.get(spotify_user_id=spotify_id)
        user_id = existing_user.user_id
    except SpotifyUser.DoesNotExist:
        user_id = generate_unique_user_id()

    spotify_profile, created = SpotifyUser.objects.get_or_create(
        user_id=user_id,
        spotify_user_id=spotify_id,
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_expiry': timezone.now() + datetime.timedelta(seconds=expires_in or 0)
        }
    )

    if not created:
        spotify_profile.access_token = access_token
        spotify_profile.refresh_token = refresh_token
        spotify_profile.token_expiry = timezone.now() + datetime.timedelta(seconds=expires_in or 0)
        spotify_profile.save()

    request.session['spotify_user_id'] = user_id
    request.session['spotify_access_token'] = access_token

    return redirect(reverse('spotify_success'))

def spotify_success(request):
  user_id = request.session.get('spotify_user_id')
  access_token = request.session.get('spotify_access_token')

  display_name = None
  if access_token:
    display_name = spotify.get_spotify_display_name(access_token)
    
  context = {
    'user_id': user_id,
    'display_name': display_name
  }

  return render(request, 'site/spotify_success.html', context)

def username_to_id(request):
  html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Roblox Username to ID Converter</title>
</head>
<body>
  <h1>Roblox Username to ID Converter</h1>
  <p>Enter a Roblox username:</p>
  <input type="text" id="usernameInput">
  <button onclick="convertUsernameToId()">Convert</button>
  <p id="result"></p>

  <script>
    function convertUsernameToId() {
      var username = document.getElementById('usernameInput').value;
      var resultParagraph = document.getElementById('result');

      if (!username) {
        resultParagraph.textContent = 'Please enter a Roblox username.';
        return;
      }

      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/roblox/convert-username-to-id/' + username, true);

      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.isValid) {
              resultParagraph.textContent = 'Roblox ID for ' + username + ': ' + response.userId;
            } else {
              resultParagraph.textContent = 'Invalid Roblox username: ' + username;
            }
          } else {
            resultParagraph.textContent = 'Error occurred while converting the username to ID.';
          }
        }
      };

      xhr.send();
    }
  </script>
</body>
</html>
"""
  return HttpResponse(html_content)
