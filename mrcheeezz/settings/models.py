from django.db import models

class SiteSetting(models.Model):
    TITLE_SEPARATOR_CHOICES = [
        ('-', '-'),
        ("–", "–"),
        ("—", "—"),
        ("_", "_"),
        (".", "."),
        ('::', '::'),
        ('|', '|'),
        ('•', '•'),
    ]

    black_footer = models.BooleanField(default=False)
    typing_speed = models.IntegerField(default=100)
    active_upper = models.BooleanField(default=False)
    theme = models.CharField(max_length=10, default='#cf2866')
    pfp_aura = models.CharField(max_length=16, default='auto')
    game_links_enabled = models.BooleanField(default=True)
    blog_enabled = models.BooleanField(default=True)
    home_title = models.BooleanField(default=True)
    title_separator = models.CharField(max_length=5, choices=TITLE_SEPARATOR_CHOICES, default='-', verbose_name='Title Separator')
