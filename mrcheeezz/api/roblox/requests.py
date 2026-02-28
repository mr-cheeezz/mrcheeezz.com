import requests
from mrcheeezz import env
from api.credentials import get_provider_config
from mrcheeezz.log import logger


def get_xcsrf(cookie):
  if cookie is None:
    cookie = get_provider_config("roblox", "roblosecurity", fallback=env.roblox_cookie)

  response = requests.post(
    "https://auth.roblox.com/v2/logout",
    headers={"Cookie": f".ROBLOSECURITY={cookie}"}
  )

  csrf_token = response.headers.get('x-csrf-token')
  return csrf_token

def get_presence(user_id, cookie=None):
  url = "https://presence.roblox.com/v1/presence/users"

  if cookie is None:
    cookie = get_provider_config("roblox", "roblosecurity", fallback=env.roblox_cookie)

  headers = {
    "Content-Type": "application/json",
    "Cookie": f".ROBLOSECURITY={cookie}",
    "X-CSRF-Token": get_xcsrf(cookie)
  }

  body = {
    "userIds": [user_id]
  }

  response = requests.post(url, headers=headers, json=body)
  data = response.json()

  user_presences = data.get("userPresences", [])

  user_presence = user_presences[0]
  user_presence_type = user_presence.get("userPresenceType")
  last_location = user_presence.get("lastLocation")
  place_id = user_presence.get("placeId")
  universe_id = user_presence.get("universeId")

  return {
    "userPresenceType": user_presence_type,
    "lastLocation": last_location,
    "placeId": place_id,
    "universeId": universe_id
  }


def get_presence_oauth(user_id, access_token):
  url = "https://presence.roblox.com/v1/presence/users"
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
  }
  body = {"userIds": [int(user_id)]}

  response = requests.post(url, headers=headers, json=body)
  if response.status_code != 200:
    return None

  data = response.json()
  user_presences = data.get("userPresences", [])
  if not user_presences:
    return None

  user_presence = user_presences[0]
  return {
    "userPresenceType": user_presence.get("userPresenceType"),
    "lastLocation": user_presence.get("lastLocation"),
    "placeId": user_presence.get("placeId"),
    "universeId": user_presence.get("universeId"),
  }

def get_max_players(place_id):
  url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit=100&cursor="
    
  response = requests.get(url)
  data = response.json()
    
  if 'data' in data and data['data']:
    max_players = data['data'][0]['maxPlayers']
    return max_players
  else:
    return None

def get_user_from_id(user_id):
  url = "https://users.roblox.com/v1/users"
  headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  body = {
    "userIds": [user_id],
    "excludeBannedUsers": False
  }

  response = requests.post(url, headers=headers, json=body)
  data = response.json()

  name = data.get('data', [{}])[0].get('name', '')
  displayName = data.get('data', [{}])[0].get('displayName', '')

  return {
    "username": name,
    "displayName": displayName
  }

def get_id_from_user(username):
  url = "https://users.roblox.com/v1/usernames/users"
  headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  body = {
    "usernames": [username],
    "excludeBannedUsers": False
  }

  response = requests.post(url, headers=headers, json=body)
  data = response.json()

  user_id = data.get('data', [{}])[0].get('id', '')

  return {
    "userId": user_id
  }

def is_valid_roblox_user(username):
  url = 'https://users.roblox.com/v1/usernames/users'
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
  data = {
    'usernames': [username],
    'excludeBannedUsers': False
  }

  response = requests.post(url, headers=headers, json=data)

  if response.status_code == 200:
    data = response.json()
    if len(data['data']) == 0:
      return {
        'isValidUser': False,
        'userId': None
      }
    else:
      return {
        'isValidUser': True,
        'userId': data['data'][0]['id']
      }
  else:
    logger.info("Failed to check Roblox user. Status code: %s", response.status_code)
    return None
  
def get_user_data(user_id):
  url = f"https://users.roblox.com/v1/users/{user_id}"
  headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  response = requests.get(url, headers=headers)
  data = response.json()

  user_id = data.get('id', '')
  username = data.get('name', '')
  display_name = data.get('displayName', '')
  description = data.get('description', '')
  created = data.get('created', '')
  is_banned = data.get('isBanned', False)
  avatar_final = data.get('avatarFinal', False)
  avatar_url = data.get('avatarUrl', '')
  is_under_13 = data.get('isUnder13', False)
  is_13_or_older = data.get('is13OrOlder', False)

  return {
    "id": user_id,
    "username": username,
    "displayName": display_name,
    "description": description,
    "created": created,
    "isBanned": is_banned,
    "avatarFinal": avatar_final,
    "avatarUrl": avatar_url,
    "isUnder13": is_under_13,
    "is13OrOlder": is_13_or_older
  }
