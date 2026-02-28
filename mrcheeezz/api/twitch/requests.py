import requests
from mrcheeezz import env
from api.credentials import get_provider_access_token, get_provider_client_id

CLIENT_ID = env.twitch_client_id

class Helix:
    BASE_URL = "https://api.twitch.tv/helix/"

    def __init__(self):
        access_token = get_provider_access_token("twitch")
        client_id = get_provider_client_id("twitch", fallback=CLIENT_ID)
        self.headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}"
        }

    def get_stream_status(self, user_id):
        endpoint = "streams"
        params = {"user_id": user_id}

        response = requests.get(self.BASE_URL + endpoint, headers=self.headers, params=params).json()
        data = response.get('data')

        if data:
            return data[0].get('type') == 'live'
        return False

    def username_to_id(self, username):
        endpoint = "users"
        params = {"login": username}

        response = requests.get(self.BASE_URL + endpoint, headers=self.headers, params=params).json()

        users_data = response.get('data')
        if users_data:
            return users_data[0].get('id')
        else:
            return None
        
    def is_user_exists(self, username):
        endpoint = "users"
        params = {"login": username}

        response = requests.get(self.BASE_URL + endpoint, headers=self.headers, params=params).json()
        users_data = response.get('data')
        return bool(users_data)
    
    def get_followage(self, from_id, to_id):
        endpoint = "users/follows"
        params = {
            "from_id": from_id,
            "to_id": to_id
        }

        response = requests.get(self.BASE_URL + endpoint, headers=self.headers, params=params).json()
        data = response.get('data')
        if data:
            follow_timestamp = data[0].get('followed_at')
            return follow_timestamp
        return None


class Kraken:
    pass
