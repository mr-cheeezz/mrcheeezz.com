from website.info import PageHREF, User, WebsiteName, WebsiteDec, NowPlayingSize, get_pages
from website.api.twitch.stream_info import get_live_state
from website.api.steam.game import current_game
from website.api.spotify.nowplaying import is_playing
from settings.models import SiteSetting
from home.models import Home
from django.core.cache import cache
from django.db.utils import OperationalError, ProgrammingError
from api.credentials import get_provider_access_token
from api.discord_profile import fetch_discord_avatar_url
from .avatar_color import color_from_local_image, color_from_remote_image

from . import version
from . import env

NewTab = 'target="_blank"'
theme = env.theme_color
ga = env.google_analytics
url = env.url
HomeTitle = env.home_title
def _resolve_site_setting():
    try:
        return SiteSetting.objects.first()
    except (OperationalError, ProgrammingError):
        return None


def _resolve_avatar_aura(site_setting, discord_pfp_url, home_page):
    setting_value = (site_setting.pfp_aura if site_setting else env.pfp_aura) or "auto"
    value = setting_value.strip().lower()
    if value == "none":
        return None

    cache_key = "avatar_aura_color:none"
    if discord_pfp_url:
        cache_key = f"avatar_aura_color:discord:{discord_pfp_url}"
    elif home_page and home_page.pfp and home_page.pfp.name:
        cache_key = f"avatar_aura_color:local:{home_page.pfp.name}:{home_page.pfp.size}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    auto_color = None
    if discord_pfp_url:
        auto_color = color_from_remote_image(discord_pfp_url)
    elif home_page and home_page.pfp:
        try:
            auto_color = color_from_local_image(home_page.pfp.path)
        except Exception:
            auto_color = None

    # If color extraction fails, keep manual value if provided.
    resolved = auto_color or (setting_value if value not in {"", "auto"} else env.pfp_aura)
    cache.set(cache_key, resolved, timeout=3600)
    return resolved

def global_vars(request):
    site_setting = _resolve_site_setting()
    blog_enabled = site_setting.blog_enabled if site_setting else True
    base_pages = get_pages()
    pages = {
        'navbar': [page for page in base_pages['navbar'] if blog_enabled or page.get('name') != 'blog'],
        'more': list(base_pages['more']),
        'mobile': [page for page in base_pages['mobile'] if blog_enabled or page.get('name') != 'blog'],
    }
    try:
        home_page = Home.objects.first()
    except (OperationalError, ProgrammingError):
        home_page = None
    discord_pfp_url = cache.get("owner_discord_pfp_url")
    if discord_pfp_url is None:
        discord_token = get_provider_access_token("discord", fallback="")
        discord_pfp_url = fetch_discord_avatar_url(discord_token) if discord_token else ""
        cache.set("owner_discord_pfp_url", discord_pfp_url, timeout=300)
    aura = _resolve_avatar_aura(site_setting, discord_pfp_url, home_page)
    theme_value = site_setting.theme if site_setting else env.theme_color
    theme_accent = aura or theme_value

    twitch_info = {
        'is_live': False,
        'view_count': 0,
        'username': None,
        'url': None,
    }
    if env.twitch_channel_id:
        twitch_cache_key = f"twitch_live_state:{env.twitch_channel_id}"
        cached_twitch_info = cache.get(twitch_cache_key)
        if cached_twitch_info is None:
            cached_twitch_info = get_live_state(env.twitch_channel_id)
            cache.set(twitch_cache_key, cached_twitch_info, timeout=45)
        twitch_info = cached_twitch_info

    steam_game = {
        'game': current_game
    }

    spotify_info = {
        'is_playing': is_playing
    }

    return {
        'sep': site_setting.title_separator if site_setting else env.title_separator,
        'nav_href': PageHREF,
        'theme': theme_value,
        'theme_accent': theme_accent,
        'google_analytics': ga,
        'created_year': "2022",
        'url': url,
        'username': User,
        'aura': aura,
        'new_tab': NewTab,
        'website_name': WebsiteName,
        'pages': pages,
        'copy': True,
        'home': False,
        'error': False,
        'home_title': site_setting.home_title if site_setting else env.home_title,
        'about': WebsiteDec,
        'now_playing': env.NowPlayingID,
        'now_playing_border': env.now_playing_border,
        'black_footer': site_setting.black_footer if site_setting else False,
        'now_playing_size': NowPlayingSize,
        'active_upper': site_setting.active_upper if site_setting else env.active_caps,
        'show_user': env.show_user,
        'typing_speed': site_setting.typing_speed if site_setting else 100,
        'game_links_enabled': site_setting.game_links_enabled if site_setting else True,
        'blog_enabled': blog_enabled,
        'discord_pfp_url': discord_pfp_url or None,
        'server_location': env.server,
        'twitch': twitch_info,
        'steam': steam_game,
        'spotify': spotify_info,
        'version': version.version,
    }
