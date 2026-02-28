from django.http import HttpResponse
from .requests import Helix

def is_live(request, channel):
  caps = request.GET.get("caps")
  
  twitch = Helix()
  user_id = twitch.username_to_id(channel)
  if not user_id:
    return HttpResponse("Invalid username or user not found", status=404)
    
  is_live = twitch.get_stream_status(user_id)
  
  if caps == "true":
    content = "Live" if is_live else "Offline"
  else: 
    content = "live" if is_live else "offline"

  return HttpResponse(content, content_type='text/plain')

def user_to_id(request, username):
  twitch = Helix()
  user_id = twitch.username_to_id(username)
  if not user_id:
    return HttpResponse("Invalid username or user not found", status=404, content_type='text/plain')
  return HttpResponse(user_id, content_type='text/plain')

def followage(request, channel, username):
  helix = Helix()

  follower_id = helix.username_to_id(username)
  channel_id = helix.username_to_id(channel)

  follow_timestamp = helix.get_followage(follower_id, channel_id)

  if follow_timestamp:
    response_text = f"{username} has been following {channel} since {follow_timestamp}."
  else:
    response_text = f"{username} is not following {channel}."

  return HttpResponse(response_text, content_type='text/plain')