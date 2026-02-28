from django.db import models
from django.utils.text import slugify


class Bot(models.Model):
    title = models.CharField(max_length=200)
    github_repo = models.URLField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class BotInstance(models.Model):
  bot = models.ForeignKey(Bot, related_name='type_list', on_delete=models.CASCADE)
  name = models.CharField(max_length=200)
  website = models.URLField(null=True, blank=True)
  website_name = models.CharField(max_length=200, null=True, blank=True)
  streamer = models.CharField(max_length=200)
  streamer_display = models.CharField(max_length=200)
  out_of_commission = models.BooleanField(default=False)

  def __str__(self):
    return self.name
    
