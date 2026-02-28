from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Log(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
      return f'{self.timestamp} - {self.message}'

class BanRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ban_reason = models.TextField()
    mod_note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Requested Ban for {self.user.username}'
    
class Alert(models.Model):
    ALERT_TYPES = [
        ('urgent', 'Urgent'),
        ('message', 'Message'),
        ('info', 'Informational'),
    ]

    type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField(max_length=250)
    end_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.get_type_display()}: {self.message}"

    def save(self, *args, **kwargs):
        if self.type == 'message':
            Alert.objects.filter(type='message').update(end_date=timezone.now())
        super().save(*args, **kwargs)
