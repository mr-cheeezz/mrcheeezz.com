import random
import pytz
from datetime import date, datetime
import datetime
from mrcheeezz import env
from django.utils import timezone
from django.db.utils import OperationalError, ProgrammingError
from projects.models import Project
from specs.models import Spec


def _model_has_rows(model):
  try:
    return model.objects.exists()
  except (OperationalError, ProgrammingError):
    # DB tables may not exist yet during first migrate/check.
    return False

class User():
  user = env.user
  def __str__(self):
    return self.user

class Avatar():
  id = env.pfp_id
  type = env.pfp_type
  aura = env.pfp_aura

  def __str__(self):
    return {
      self.id,
      self.type,
      self.aura
    }

class WebsiteName():
  website_name = env.website_name

  def __str__(self):
    return str(self.website_name)

class Responses():
  responses = env.tw

  def __str__(self):
    return self.responses

class Location():
  country = env.Country
  state = env.State
  city = env.City

  outOfUS = env.US
  OScountry = env.OutOfUsCountry
  OScity = env.OutOfUsCity

  if country == '':
    resp = f'{city}, {state}'
  elif city == '':
    resp = f'{state} in the {country}'
  else:
    resp = f'{city}, {state} in the {country}'

  if outOfUS:
    if OScity == '':
      resp = f'{OScountry}'
    else:
      resp = f'{OScity}, {OScountry}'

  def __str__(self):
    return str(self.resp)

class TimeZone():

  def __init__(self):
    ny_tz = pytz.timezone('America/New_York')

    ny_time = timezone.now().astimezone(ny_tz)

    self.tz_name = ny_time.strftime('%Z')

  def __str__(self):
    return self.tz_name


class WelcomeMsg():
    messages = {
        "morning": "Good morning",
        "afternoon": "Good afternoon",
        "evening": "Good evening",
        "night": "Good night"
    }

    def __init__(self):
        self.welcome = self.get_welcome_message()

    def get_welcome_message(self):
        current_time = datetime.datetime.now().time()

        if current_time < datetime.time(12, 0): 
            return self.messages["morning"]
        elif current_time < datetime.time(18, 0):
            return self.messages["afternoon"]
        elif current_time < datetime.time(21, 0):
            return self.messages["evening"]
        else:
            return self.messages["night"]

    def __str__(self):
        return self.welcome

class Programming():
  y = env.programming_start

  if y == '':
    start = None  # or any default value that makes sense in your context
  else:
    start = int(y)

  current_year = datetime.datetime.now().year
  if start is not None:
    since = current_year - start
  else:
    since = None  # or any default value that makes sense in your context

  def __str__(self):
    return str(self.start), str(self.since)

class NowPlaying():
  NowPlayingId = env.NowPlayingID

  def __str__(self):
    return self.NowPlayingId

class NowPlayingSize():
  npz = env.now_playing_size
  custom = env.now_playing_size_c
  default = '1'

  if npz == 1:
    size = default
  elif npz == 2:
    size = '1.15'
  elif npz == 3:
    size = '1.2'
  elif npz == 4:
    size = '1.3'
  elif npz == 5:
    size = '2'
  elif npz == 10:
    size = custom
  else:
    size = '[Number Lower Than 1 - 5 or 10]'

  def __str__(self):
    return str(self.size)

class FavArtist():
  link = env.artist_url
  name = env.ArtistName
  song = env.SongName
  songlink = env.song_url

  def __str__(self):
    return {
      self.link,
      self.name,
      self.song,
      self.songlink
    }

def get_pages():
  navbar = [
    {'name': 'about'},
    {'name': 'blog'},
    {'name': 'api'},
    {'name': 'contact'},
  ]

  more = [
    {'name': 'projects', 'js': True} if _model_has_rows(Project) else None,
    {'name': 'bots', 'js': True} if env.twitch_bots else None,
    {'name': 'specs', 'js': True},
    {'name': 'upload', 'js': True},
    {'name': 'Twitch Logs', 'link': '/redirect?url=https://logs.mrcheeezz.com'},
    {'name': 'Twitch Bot', 'link': '/redirect?url=https://bot.mrcheeezz.com'},
  ]

  mobile = [
      {'name': 'about', 'link': '/about'},
      {'name': 'blog', 'link': '/blog/'},
      {'name': 'api', 'link': '/api/'},
      {'name': 'contact', 'link': '/contact'},
      {'name': 'projects', 'link': '/projects'} if _model_has_rows(Project) else None,
      {'name': 'bots', 'link': '/bots'} if env.twitch_bots else None,
      {'name': 'specs', 'link': '/specs/'},
      {'name': 'upload', 'link': '/upload'},
      {'name': 'Twitch Logs', 'link': '/redirect?url=https://logs.mrcheeezz.com'},
      {'name': 'Twitch Bot', 'link': '/redirect?url=https://bot.mrcheeezz.com'},
  ]

  return {
    'navbar': navbar,
    'more': [item for item in more if item is not None],
    'mobile': [item for item in mobile if item is not None],
  }

class Pages():

  navbar = [
    {'name': 'about'},
    {'name': 'blog'},
    {'name': 'api'},
    {'name': 'contact'},
  ]

  more = [
    {'name': 'projects', 'js': True} if _model_has_rows(Project) else None,
    {'name': 'bots', 'js': True} if env.twitch_bots else None,
    {'name': 'specs', 'js': True} if _model_has_rows(Spec) else None,
    {'name': 'upload', 'js': True},
    {'name': 'Twitch Logs', 'link': '/redirect?url=https://logs.mrcheeezz.com'},
    {'name': 'Twitch Bot', 'link': '/redirect?url=https://bot.mrcheeezz.com'}
  ]

  more = [item for item in more if item is not None]

  mobile = [
      {'name': 'about', 'link': '/about'},
      {'name': 'blog', 'link': '/blog/'},
      {'name': 'api', 'link': '/api/'},
      {'name': 'contact', 'link': '/contact'},
      {'name': 'projects', 'link': '/projects'} if _model_has_rows(Project) else None,
      {'name': 'bots', 'link': '/bots'} if env.twitch_bots else None,
      {'name': 'specs', 'link': '/specs/'} if _model_has_rows(Spec) else None,
      {'name': 'upload', 'link': '/upload'},
      {'name': 'Twitch Logs', 'link': '/redirect?url=https://logs.mrcheeezz.com'},
      {'name': 'Twitch Bot', 'link': '/redirect?url=https://bot.mrcheeezz.com'}
  ]

  mobile = [item for item in mobile if item is not None]

  def __str__(self):
    return {
      self.navbar,
      self.more,
      self.mobile
    }

class WebsiteDec():
  dec = f"Hey I'm {env.user}, Welcome to my website!"
  def __str__(self):
    return str(self.dec)

class Bots():

  PB = [
    {'streamer': 'Mr_Cheeezz', 'name': 'FeelsWeirdBot', 'link': 'mrcheeezz.xyz'},
    {'streamer': 'Tibb12', 'name': 'FeelsWeirdBot', 'link': 'tibb12.tv'},
    {'streamer': 'Junglaxr', 'name': 'JunglaxrBot', 'link': 'bot.junglaxr.com'},
    {'streamer': 'Sin_Exalted', 'name': 'FeelsCreamyBot', 'link': 'sinexalted.feelsweirdbot.com'},
    {'streamer': 'PowerTheEnrgyy', 'name': 'PowerTheBot', 'link': 'powertheenrgyy.feelsweirdbot.com'},
  ]


PageHREF = [
  {
    'name': 'home',
    'link': '',
  },
  {
    'name': 'contact',
    'link': 'contact',
  },
  {
    'name': 'blog',
    'link': 'blog',
  },
  {
    'name': 'about',
    'link': 'about',
  },
  {
    'name': 'bots',
    'link': 'bots',
  },
  {
    'name': 'projects',
    'link': 'projects',
  },
  {
    'name': 'specs',
    'link': 'specs',
  },
  {
    'name': 'upload',
    'link': 'upload',
  },
]

BotList = [
  {
    'heading': 'FeelsWeirdBot',
    'url': 'https://mrcheeezz.xyz',
    'link_text': 'mrcheeezz.xyz',
    'user_link': 'mr_cheeezz',
    'user_text': 'Mr_Cheeezz',
  },
  {
    'heading': 'BasementHelper',
    'url': 'https://tibb12.tv',
    'link_text': 'tibb12.tv',
    'user_link': 'tibb12',
    'user_text': 'tibb12',
  },
  {
    'heading': 'JunglaxrBot',
    'url': 'https://bot.junglaxr.com',
    'link_text': 'bot.junglaxr.com',
    'user_link': 'junglaxr',
    'user_text': 'Junglaxr',
  },
  {
    'heading': 'TibbHubby',
    'url': 'https://maycris.feelsweirdbot.com',
    'link_text': 'maycris.feelsweirdbot.com',
    'user_link': 'maycris',
    'user_text': 'Maycris',
  },
  {
    'heading': 'FeelsCreamyBot',
    'url': 'https://sinexalted.feelsweirdbot.com',
    'link_text': 'sinexalted.feelsweirdbot.com',
    'user_link': 'sin_exalted',
    'user_text': 'Sin_Exalted',
  },
  {
    'heading': 'PowerTheBot',
    'url': 'https://sinexalted.feelsweirdbot.com',
    'link_text': 'powertheenrgyy.feelsweirdbot.com',
    'user_link': 'powertheenrgyy',
    'user_text': 'PowerTheEnrgyy',
  },
]

class Age:
  def __init__(self):
    y = env.birth_year
    m = env.birth_month
    d = env.birth_day

    today = date.today()
    birthdate = date(y, m, d)
    self.age = today.year - y - ((today.month, today.day) < (m, d))

  def __str__(self):
    return str(self.age)

class Show():
  location = env.show_location
  age = env.show_age
  spotify = env.show_now_playing

  def __str__(self):
    return {
      self.location,
      self.age,
      self.spotify,
    }
