from django.db import models

class Contact(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField()
  url = models.CharField(max_length=50, null=True, blank=True)
  display = models.CharField(max_length=200, null=True, blank=True)
  user = models.CharField(max_length=200, null=True, blank=True)
  server = models.URLField(null=True, blank=True)

  def __str__(self):
    return self.title
