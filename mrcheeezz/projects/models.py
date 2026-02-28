from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class Tag(models.Model):
  name = models.CharField(max_length=50)

  def __str__(self):
    return self.name

class FAQ(models.Model):
  question = models.TextField()
  answer = models.TextField()

  def __str__(self):
    return self.question

class InstallInstruction(models.Model):
  instruction = models.TextField()

  def __str__(self):
    return self.instruction

class KnownIssue(models.Model):
  issue = models.TextField()

  def __str__(self):
    return self.issue

class Feature(models.Model):
  feature = models.TextField()

  def __str__(self):
    return self.feature

class Project(models.Model):
  name = models.CharField(max_length=50)
  created_at = models.DateTimeField(default=timezone.now)
  slug = models.SlugField(max_length=50, unique=True, blank=True)
  body = models.TextField()
  github_url = models.URLField(max_length=75, default='https://github.com/')
  date = models.DateTimeField(auto_now_add=False)
  author = models.CharField(max_length=50)
  language = models.CharField(max_length=30)
  tags = models.ManyToManyField(Tag)
  image = models.ImageField(upload_to='projects', null=True, blank=True)
  image_caption = models.CharField(max_length=50, null=True)
  install_instructions = models.ManyToManyField(InstallInstruction)
  features = models.ManyToManyField(Feature)
  known_issues = models.ManyToManyField(KnownIssue)
  faqs = models.ManyToManyField(FAQ) 

  def __str__(self):
    return self.name
  
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super(Project, self).save(*args, **kwargs)
