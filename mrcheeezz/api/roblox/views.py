from django.http import HttpResponse, JsonResponse
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
from . import requests as roblox
from mrcheeezz import env
from api.credentials import get_provider_config
from datetime import datetime, timedelta

@csrf_exempt
@ratelimit(key='ip', rate='20/m', block=True)
def presence(request, username):
  show_user = request.GET.get('show_user')
  use_display_name = request.GET.get('use_display')

  if not username:
    return HttpResponse('Roblox username (username) query parameter is required', status=400, content_type='text/plain')

  roblox_user_info = roblox.is_valid_roblox_user(username)

  if not roblox_user_info['isValidUser']:
    return HttpResponse('Invalid Roblox username', status=400, content_type='text/plain')

  try:
    roblox_cookie = get_provider_config("roblox", "roblosecurity", fallback=env.roblox_cookie)
    roblox_id = roblox_user_info['userId']

    presence_data = roblox.get_presence(roblox_id, roblox_cookie)

    location = presence_data.get("lastLocation", "Unknown")
    onlineStatus = presence_data.get("userPresenceType", 0)

    if show_user:
      user_info = roblox.get_user_from_id(roblox_id)
      username = user_info.get("username")
      display_name = user_info.get("displayName")

      if onlineStatus == 0:
        user_description = display_name if use_display_name and display_name else username
        location = f"{user_description} is currently offline"
      else:
        if location == 'Website':
          location_description = 'on the Website'
        else:
          location_description = f'playing {location}'

          if use_display_name:
            user_description = display_name if display_name else username
          else:
            user_description = username

          location = f"{user_description} is currently {location_description}"
    else:
      if onlineStatus == 0:
        location = 'Offline'
      else:
        if location == 'Website':
          location = 'Website'
        else:
          if location == "":
            location = 'Unable to fetch current presence'
          else:
            location = f'{location}'


    return HttpResponse(location, content_type='text/plain')

  except Exception as e:
    return HttpResponse(str(e), status=500, content_type='text/plain')

@csrf_exempt
@ratelimit(key='ip', rate='5/m', block=True)
def max_players(request, type, id):
    try:
        if type == "user_based":
            roblox_id = int(id)
            
            presence_data = roblox.get_presence(roblox_id)
            place_id = presence_data.get("placeId", None)

            user_info = roblox.get_user_from_id(roblox_id)
            username = user_info.get("username")

            location = presence_data.get("lastLocation", "Unknown")

            if place_id is not None:
                if "Criminality" in location:
                    max_players = roblox.get_max_players("4588604953")
                    max_players = max_players - 10
                else: 
                    max_players = roblox.get_max_players(place_id)
                response_content = f"The max players for {location} is {max_players}"
            else:
                response_content = f"No place ID found for User {username}"

        elif type == "game_based":
            place_id = int(id)
            max_players = roblox.get_max_players(place_id)
            response_content = f"Max Players for Place ID {place_id}: {max_players}"

        else:
            return HttpResponse('Invalid type parameter', status=400, content_type='text/plain')

        return HttpResponse(response_content, content_type='text/plain')

    except Exception as e:
        return HttpResponse(str(e), status=500, content_type='text/plain')

@csrf_exempt
def convert_username_to_id(request, username):
  try:
    roblox_user_info = roblox.is_valid_roblox_user(username)
    if not roblox_user_info['isValidUser']:
      return JsonResponse({'isValid': False, 'userId': None})

    roblox_id = roblox_user_info['userId']

    return JsonResponse({'isValid': True, 'userId': roblox_id})

  except Exception as e:
    return JsonResponse({'isValid': False, 'userId': None})
  
@csrf_exempt
@ratelimit(key='ip', rate='10/m', block=True)
def user_info(request, type, username):  
  roblox_user_info = roblox.is_valid_roblox_user(username)

  if not roblox_user_info['isValidUser']:
    return HttpResponse('Invalid Roblox username', status=400, content_type='text/plain')
    
  try:
    roblox_cookie = get_provider_config("roblox", "roblosecurity", fallback=env.roblox_cookie)
    roblox_id = roblox_user_info['userId']

    presence_data = roblox.get_presence(roblox_id, roblox_cookie)
    user_data = roblox.get_user_data(roblox_id)

    location = presence_data.get("lastLocation", "Unknown")
    onlineStatus = presence_data.get("userPresenceType", 0)
    user = user_data.get("username", "Unknown")
    display = user_data.get("displayName")
    description = user_data.get("description", "No description available")

    created_iso = user_data.get("created")
    created_date = datetime.fromisoformat(created_iso.split("T")[0])
    formatted_created = created_date.strftime('%Y-%m-%d')

    today = datetime.now()
    age_delta = today - created_date

    if age_delta.days < 1:
      age_str = "Less Than a Day"
    else:
      years = age_delta.days // 365
      months = (age_delta.days % 365) // 30
      days = (age_delta.days % 365) % 30
      age_str_parts = []
      if years:
        age_str_parts.append(f"{years}Y")
      if months:
        age_str_parts.append(f"{months}M")
      age_str_parts.append(f"{days}D")
      age_str = "".join(age_str_parts)

    isBanned = user_data.get("isBanned")
    isUnder13 = user_data.get("isUnder13")

    if type == 'location':
      return HttpResponse(location, content_type='text/plain')
    elif type == 'onlineStatus':
      return HttpResponse(str(onlineStatus), content_type='text/plain')
    elif type == 'user':
      return HttpResponse(user, content_type='text/plain')
    elif type == 'display':
      return HttpResponse(display, content_type='text/plain')
    elif type == 'created':
      return HttpResponse(formatted_created, content_type='text/plain')
    elif type == 'description':
      return HttpResponse('User is banned!' if isBanned else description, content_type='text/plain')
    elif type == 'isBanned':
      return HttpResponse('yes' if isBanned else 'no', content_type='text/plain')
    elif type == 'isUnder13':
      return HttpResponse('yes' if isUnder13 else 'no', content_type='text/plain')
    elif type == 'all':
      if location != "Website":
        status = f'playing {location}'
      elif onlineStatus == 0:
        status = 'Offline'
      banned_str = 'yes' if isBanned else 'no'
      under13_str = 'yes' if isUnder13 else 'no'
      body = f"Username - {user} | Status - {status} | Description - {description} | Created - {formatted_created} ({age_str}) | Banned - {banned_str} | Under 13 - {under13_str}"
      return HttpResponse(body, content_type='text/plain')
    else:
      return HttpResponse('Invalid type parameter', status=400, content_type='text/plain')

  except Exception as e:
    return HttpResponse(str(e), status=500, content_type='text/plain')
