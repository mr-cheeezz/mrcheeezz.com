from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class Part(models.Model):
  part = models.CharField(max_length=100)
  part_name = models.CharField(max_length=100)

  def __str__(self):
    return self.part_name

class Spec(models.Model):
  name = models.CharField(max_length=100)
  created_at = models.DateTimeField(default=timezone.now)
  slug = models.SlugField(null=True, blank=True)
  icon = models.CharField(max_length=50)
  parts = models.ManyToManyField(Part)
  pic = models.ImageField(upload_to='specs', null=True, blank=True)
  pic_alt = models.CharField(max_length=200, null=True, blank=True)
  pic2 = models.ImageField(upload_to='specs', null=True, blank=True)
  pic2_alt = models.CharField(max_length=200, null=True, blank=True)
  pic_count = models.IntegerField(default=0)

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name
