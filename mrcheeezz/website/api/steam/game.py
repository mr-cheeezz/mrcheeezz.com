import requests
from mrcheeezz import env
from mrcheeezz.log import logger

STEAM_API_KEY = env.steam_api_key
STEAM_USER_ID = env.steam_user_id

def check_current_game_status(steam_user_id):
    if not steam_user_id or not STEAM_API_KEY:
        return None

    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_user_id}'
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
        logger.info("Steam API error on current game lookup: %s", response.status_code)
        return None

current_game = check_current_game_status(STEAM_USER_ID)

