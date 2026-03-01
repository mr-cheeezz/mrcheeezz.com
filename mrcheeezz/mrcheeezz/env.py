from configparser import ConfigParser
from pathlib import Path
from datetime import datetime
import json
import locale
import os
from urllib import request as urllib_request


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(os.getenv("MRCHEEEZZ_CONFIG", ROOT_DIR / "config.ini"))

_config = ConfigParser(interpolation=None)
if CONFIG_PATH.exists():
    _config.read(CONFIG_PATH)


def _get_str(section, key, default=""):
    return _config.get(section, key, fallback=str(default)).strip()


def _get_bool(section, key, default=False):
    try:
        return _config.getboolean(section, key, fallback=default)
    except ValueError:
        return default


def _get_int(section, key, default=0):
    try:
        return _config.getint(section, key, fallback=default)
    except ValueError:
        return default


def _get_list(section, key, default=""):
    raw = _get_str(section, key, default)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _get_str_multi(pairs, default=""):
    for section, key in pairs:
        if _config.has_option(section, key):
            return _get_str(section, key, default)
    return str(default).strip()


# Basic
user = _get_str("basic", "user", "Mr_Cheeezz")
name = _get_str("basic", "name", user)
beta = _get_bool("basic", "beta", False)
github_pat = _get_str("basic", "github_pat", "")
branch = _get_str("basic", "branch", "master")
show_user = _get_bool("basic", "show_user", True)
website_name = _get_str("basic", "website_name", "Mr_Cheeezz")
base_name = _get_str("basic", "base_name", "mrcheeezz")
url = _get_str("basic", "url", "localhost")
debug = _get_bool("basic", "debug", False)
allowed_hosts = _get_list("basic", "allowed_hosts", url)
cors_allowed_origins = _get_list("basic", "cors_allowed_origins", f"https://{url}")
secret_key = _get_str("basic", "secret_key", "unsafe-local-secret-key")
discord_user = _get_str("basic", "discord_user", "mr_cheeezz")
twitch_bots = _get_bool("basic", "twitch_bots", True)

# Contact / legal placeholders (used in update views)
location = _get_str("basic", "location", "")
server = _get_str("basic", "server", "")
email = _get_str("basic", "email", "")
pub_email = _get_str("basic", "pub_email", "")

# Database
postgresql_user = _get_str("database", "postgresql_user", "postgres")
postgresql_password = _get_str("database", "postgresql_password", "")
use_sqlite = _get_bool("database", "use_sqlite", False)
postgresql_name = _get_str("database", "postgresql_name", "website")
postgresql_host = _get_str("database", "postgresql_host", "localhost")
postgresql_port = _get_str("database", "postgresql_port", "5432")

# General site options
programming_start = _get_str("site", "programming_start", "2018")
home_title = _get_bool("site", "home_title", True)
tw = _get_str(
    "site",
    "tw",
    '"I code in different computer languages.", "I\'m a student who keeps learning.", "I edit videos and photos.", "I enjoy making things as a developer."',
)
theme_color = _get_str("site", "theme_color", "#fe5186")
pfp_type = _get_str("site", "pfp_type", "gif")
avatar_id = _get_int("site", "avatar_id", 1)
pfp_id = _get_str("site", "pfp_id", str(avatar_id))
pfp_aura = _get_str("site", "pfp_aura", "red")
active_caps = _get_bool("site", "active_caps", True)
title_separator = _get_str_multi(
    [
        ("site", "title_separator"),
        ("site", "title_seperator"),
    ],
    "-",
)
# Backward compatibility alias.
title_seperator = title_separator
svg_size = _get_str("site", "svg_size", "27")
welcome_messages = _get_str(
    "site",
    "welcome_messages",
    "Hello,Hey,Greetings,Salutations,Howdy,Hiya,Aloha,Bonjour,Hola,Yo,Top of the morning to you,G'day mate,Salam,Konnichiwa",
)
border_glow = _get_bool("site", "border_glow", True)
show_specs = _get_bool("site", "show_specs", True)

# Storage
media_root = _get_str("storage", "media_root", str(ROOT_DIR / "uploads"))
media_url = _get_str("storage", "media_url", "/media/")
if not media_url.startswith("/"):
    media_url = f"/{media_url}"
if not media_url.endswith("/"):
    media_url = f"{media_url}/"

# Integrations / app credentials
google_analytics = _get_str_multi(
    [
        ("analytics", "google_analytics"),
        ("third_party", "google_analytics"),
    ],
    "",
)

NowPlayingID = _get_str_multi(
    [
        ("spotify", "now_playing_user_id"),
        ("third_party", "NowPlayingID"),
    ],
    "",
)

twitch_client_id = _get_str_multi(
    [
        ("twitch", "client_id"),
        ("third_party", "twitch_client_id"),
    ],
    "",
)
twitch_client_secret = _get_str_multi(
    [
        ("twitch", "client_secret"),
        ("third_party", "twitch_client_secret"),
    ],
    "",
)
# Runtime tokens are stored in DB (APICredential), not in config.
access_token = ""
twitch_channel_id = _get_str_multi(
    [
        ("twitch", "channel_id"),
        ("third_party", "twitch_channel_id"),
    ],
    "",
)

# Discord OAuth app config
discord_client_id = _get_str_multi(
    [
        ("discord", "client_id"),
    ],
    "",
)
discord_client_secret = _get_str_multi(
    [
        ("discord", "client_secret"),
    ],
    "",
)
discord_redirect_uri = _get_str_multi(
    [
        ("discord", "redirect_uri"),
    ],
    "",
)

steam_api_key = _get_str_multi(
    [
        ("steam", "api_key"),
        ("third_party", "steam_api_key"),
    ],
    "",
)
steam_user_id = _get_str_multi(
    [
        ("steam", "user_id"),
        ("third_party", "steam_user_id"),
    ],
    "",
)

NPSSO_TOKEN = _get_str_multi(
    [
        ("playstation", "npsso_token"),
        ("third_party", "NPSSO_TOKEN"),
    ],
    "",
)

consumer_key = _get_str_multi(
    [
        ("twitter", "consumer_key"),
        ("third_party", "consumer_key"),
    ],
    "",
)
consumer_secret = _get_str_multi(
    [
        ("twitter", "consumer_secret"),
        ("third_party", "consumer_secret"),
    ],
    "",
)
twitter_access_token = ""
twitter_access_token_secret = ""
twitter_handle = _get_str_multi(
    [
        ("twitter", "handle"),
        ("third_party", "twitter_handle"),
    ],
    "",
)
twitter_bearer_token = _get_str_multi(
    [
        ("twitter", "bearer_token"),
        ("third_party", "twitter_bearer_token"),
    ],
    "",
)

spotify_client_id = _get_str_multi(
    [
        ("spotify", "client_id"),
        ("spotify", "spotify_clinet_id"),
        ("third_party", "spotify_clinet_id"),
    ],
    "",
)
spotify_client_secret = _get_str_multi(
    [
        ("spotify", "client_secret"),
        ("spotify", "spotify_clinet_secret"),
        ("third_party", "spotify_clinet_secret"),
    ],
    "",
)
# Backward compatibility aliases.
spotify_clinet_id = spotify_client_id
spotify_clinet_secret = spotify_client_secret
spotify_redirect_uri = _get_str_multi(
    [
        ("spotify", "redirect_uri"),
        ("third_party", "spotify_redirect_uri"),
    ],
    "",
)

# Roblox OAuth app config + cookie fallback for public Roblox endpoints.
roblox_oauth_client_id = _get_str_multi(
    [
        ("roblox", "oauth_client_id"),
    ],
    "",
)
roblox_oauth_client_secret = _get_str_multi(
    [
        ("roblox", "oauth_client_secret"),
    ],
    "",
)
roblox_oauth_redirect_uri = _get_str_multi(
    [
        ("roblox", "oauth_redirect_uri"),
    ],
    "",
)
roblox_oauth_scope = _get_str_multi(
    [
        ("roblox", "oauth_scope"),
    ],
    "openid profile",
)

roblox_user = _get_str_multi(
    [
        ("roblox", "user"),
        ("third_party", "roblox_user"),
    ],
    "",
)
roblox_cookie = _get_str_multi(
    [
        ("roblox", "roblosecurity"),
        ("roblox", "cookie"),
        ("third_party", "roblox_cookie"),
    ],
    "",
)

discord_access_token = ""

# Location
Country = _get_str("location", "Country", "US")
State = _get_str("location", "State", "")
City = _get_str("location", "City", "")
if _config.has_option("location", "US"):
    US = _get_bool("location", "US", False)
else:
    US = Country.strip().upper() in {"US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"}
OutOfUsCountry = _get_str("location", "OutOfUsCountry", "")
OutOfUsCity = _get_str("location", "OutOfUsCity", "")
show_location = _get_bool("location", "show_location", True)


def _join_location_parts(parts):
    cleaned = [str(part).strip() for part in parts if str(part).strip()]
    return ", ".join(cleaned)


def _config_location_fallback():
    if US:
        country = Country
        if country.strip().upper() in {"US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"}:
            country = "USA"
        return _join_location_parts([City, State, country])

    city = OutOfUsCity or City
    country = OutOfUsCountry or Country
    return _join_location_parts([city, country])


def _timezone_location_fallback():
    city = ""
    try:
        tzinfo = datetime.now().astimezone().tzinfo
        tz_name = getattr(tzinfo, "key", "") or str(tzinfo or "")
        if "/" in tz_name:
            city = tz_name.split("/")[-1].replace("_", " ").strip()
    except Exception:
        city = ""

    country_code = ""
    try:
        locale_name = locale.getlocale()[0] or ""
        if "_" in locale_name:
            country_code = locale_name.split("_", 1)[1].strip()
    except Exception:
        country_code = ""

    derived = _join_location_parts([city, country_code])
    return derived or "Local Server Region"


def _extract_location_from_payload(payload):
    city = str(payload.get("city", "")).strip()
    region = str(payload.get("region", "")).strip() or str(payload.get("region_name", "")).strip()
    country = (
        str(payload.get("country_name", "")).strip()
        or str(payload.get("country", "")).strip()
        or str(payload.get("country_code", "")).strip()
    )
    return _join_location_parts([city, region, country])


def _ip_location_fallback():
    providers = [
        ("https://ipapi.co/json/", None),
        ("https://ipwho.is/", "success"),
    ]

    for endpoint, success_key in providers:
        try:
            with urllib_request.urlopen(endpoint, timeout=2.5) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            if success_key and not payload.get(success_key, False):
                continue
            resolved = _extract_location_from_payload(payload)
            if resolved:
                return resolved
        except Exception:
            continue
    return ""


def resolve_general_host_location():
    ip_location = _ip_location_fallback()
    if ip_location:
        return ip_location
    return _timezone_location_fallback()


def resolve_owner_location():
    if location:
        return location
    config_value = _config_location_fallback()
    if config_value:
        return config_value
    return resolve_general_host_location()


# Final values used by legal/footer placeholders.
location = resolve_owner_location()
server = resolve_general_host_location()

# Age
birth_year = _get_int("age", "birth_year", 2000)
birth_month = _get_int("age", "birth_month", 1)
birth_day = _get_int("age", "birth_day", 1)
show_age = _get_bool("age", "show_age", True)

# Spotify / now playing
# Legacy favorite-artist values (deprecated; kept for backward compatibility).
ArtistName = _get_str("spotify", "ArtistName", "")
artist_url = _get_str_multi(
    [
        ("spotify", "artist_url"),
        ("spotify", "AristUrl"),
    ],
    "",
)
SongName = _get_str("spotify", "SongName", "")
song_url = _get_str_multi(
    [
        ("spotify", "song_url"),
        ("spotify", "SongUrl"),
    ],
    "",
)
# Backward compatibility aliases.
AristUrl = artist_url
SongUrl = song_url
now_playing_border = _get_bool("spotify", "now_playing_border", False)
now_playing_size = _get_int("spotify", "now_playing_size", 1)
now_playing_size_c = _get_str("spotify", "now_playing_size_c", "1.0")
show_now_playing = _get_bool("spotify", "show_now_playing", True)
