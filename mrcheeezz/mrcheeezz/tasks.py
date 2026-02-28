from celery import shared_task
import requests
from . import env
from .log import logger

STEAM_API_KEY = env.steam_api_key
STEAM_USER_ID = env.steam_user_id

@shared_task
def check_current_game_status():
    if not STEAM_API_KEY or not STEAM_USER_ID:
        return None

    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={STEAM_USER_ID}'
    try:
        response = requests.get(url, timeout=8)
    except requests.RequestException:
        return None

    if response.status_code == 200:
        data = response.json()
        if 'response' in data and 'players' in data['response']:
            players = data['response']['players']
            if players:
                player = players[0]
                if 'gameextrainfo' in player:
                    return player['gameextrainfo']
                else:
                    return None
    else:
        logger.info("Steam API error in task check_current_game_status: %s", response.status_code)
        return None
