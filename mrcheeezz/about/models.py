from django.db import models
from datetime import date, datetime

class About(models.Model):
  title = models.CharField(max_length=200)
  content = models.TextField()

  def __str__(self):
    return self.title
  
class ProgrammingLanguage(models.Model):
  name = models.CharField(max_length=255)
  link = models.URLField()

  def __str__(self):
    return self.name
    
class Settings(models.Model):
  use = models.BooleanField(default=False)

  show_location = models.BooleanField(default=False)
  country = models.CharField(max_length=255, blank=True, null=True)
  state = models.CharField(max_length=255, blank=True, null=True)
  city = models.CharField(max_length=255, blank=True, null=True)

  show_age = models.BooleanField(default=False)
  birth_year = models.IntegerField(blank=True, null=True)
  birth_month = models.IntegerField(blank=True, null=True)
  birth_day = models.IntegerField(blank=True, null=True)

  programming_start = models.IntegerField(blank=True, null=True)
  programming_languages = models.ManyToManyField(ProgrammingLanguage)

  artist = models.CharField(max_length=50, blank=True, null=True)
  song = models.CharField(max_length=50, blank=True, null=True)

  baseball = models.CharField(max_length=100, blank=True, null=True)
  nfl = models.CharField(max_length=100, blank=True, null=True)
  col_fbl = models.CharField(max_length=100, blank=True, null=True)
  hockey = models.CharField(max_length=100, blank=True, null=True)

  movie = models.CharField(max_length=255, blank=True, null=True)
  movie_platform = models.CharField(max_length=255, blank=True, null=True)
  tv_show = models.CharField(max_length=255, blank=True, null=True)
  tv_show_platform = models.CharField(max_length=255, blank=True, null=True)

  def formatted_location(self):
    location_parts = [part for part in [self.city, self.state, self.country] if part]

    if not location_parts:
      return "Location not specified"

    return ", ".join(location_parts)
  
  def formatted_age(self):
    y = self.birth_year
    m = self.birth_month
    d = self.birth_day

    today = date.today()
    birthdate = date(y, m, d)
    age = today.year - y - ((today.month, today.day) < (m, d))

    return age
  
  def programming_time(self):
    if self.programming_start == '':
      return "[START IS NOT DEFINED]"
    current_year = datetime.now().year
    programming_time = current_year - self.programming_start

    return programming_time

  def to_dict(self):
    location_value = self.formatted_location()
    try:
      age_value = self.formatted_age() if self.show_age and self.birth_year and self.birth_month and self.birth_day else None
    except Exception:
      age_value = None
    try:
      programming_time_value = self.programming_time() if self.programming_start else None
    except Exception:
      programming_time_value = None

    settings_dict = {
      'set_up': self.use,
      'show': {
        'location': self.show_location,
        'age': self.show_age,
      },
      'programming_languages': [
        {'name': lang.name, 'link': lang.link}
        for lang in self.programming_languages.all()
      ],
      'favorite': {
        'sport': {
          'baseball': self.baseball,
          'nfl_football': self.nfl,
          'college_football': self.col_fbl,
          'hockey': self.hockey,
        },
        'song': {
          'name': self.song,
          'artist': self.artist,
        }
      },
      'programming': {
        'start': self.programming_start,
        'time': programming_time_value,
      },
      'location': location_value,
      'age': age_value,
    }

    return settings_dict

  def __str__(self):
    return "About Settings"
