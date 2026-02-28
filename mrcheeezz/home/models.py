import os
import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


SOCIAL_PRESETS = {
    "discord": {"label": "Discord", "color": "#5865F2", "icon_class": "fa-brands fa-discord"},
    "spotify": {"label": "Spotify", "color": "#1DB954", "icon_class": "fa-brands fa-spotify"},
    "twitch": {"label": "Twitch", "color": "#9146FF", "icon_class": "fa-brands fa-twitch"},
    "youtube": {"label": "YouTube", "color": "#FF0000", "icon_class": "fa-brands fa-youtube"},
    "github": {"label": "GitHub", "color": "#ffffff", "icon_class": "fa-brands fa-github"},
    "steam": {"label": "Steam", "color": "#66C0F4", "icon_class": "fa-brands fa-steam"},
    "twitter": {"label": "X/Twitter", "color": "#ffffff", "icon_class": "fa-brands fa-x-twitter"},
    "instagram": {"label": "Instagram", "color": "#E1306C", "icon_class": "fa-brands fa-instagram"},
    "reddit": {"label": "Reddit", "color": "#FF4500", "icon_class": "fa-brands fa-reddit"},
    "website": {"label": "Website", "color": "#fe5186", "icon_class": "fa-solid fa-link"},
}


SOCIAL_PLATFORM_CHOICES = [(key, value["label"]) for key, value in SOCIAL_PRESETS.items()]

class Social(models.Model):
    platform = models.CharField(max_length=32, choices=SOCIAL_PLATFORM_CHOICES, default="website")
    link = models.CharField(max_length=255)
    title = models.CharField(max_length=50, blank=True)
    id = models.SlugField(primary_key=True)
    svg = models.FileField(upload_to='icons/', blank=True, null=True)
    color = models.CharField(max_length=14, blank=True)
    enabled = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.title + ' Icon'

    @property
    def icon_class(self):
        return SOCIAL_PRESETS.get(self.platform, SOCIAL_PRESETS["website"])["icon_class"]

    def save(self, *args, **kwargs):
        preset = SOCIAL_PRESETS.get(self.platform, SOCIAL_PRESETS["website"])
        self.title = preset["label"]
        self.color = preset["color"]
        if not self.id:
            self.id = f"{slugify(self.platform)}-{uuid.uuid4().hex[:8]}"
        return super().save(*args, **kwargs)
    
def avatar_location(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    uniq_filename = '{}{}'.format(uuid.uuid4(), file_extension)
    return 'avatar/{}'.format(uniq_filename)

class Home(models.Model):
    pfp = models.ImageField(upload_to=avatar_location)

    def save(self, *args, **kwargs):
        if self.pk is None and Home.objects.exists():
            raise ValidationError('There can be only one Home instance')
        return super(Home, self).save(*args, **kwargs)
