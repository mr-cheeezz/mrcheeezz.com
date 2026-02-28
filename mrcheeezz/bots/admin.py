from django.contrib import admin

from .models import  Bot, BotInstance


admin.site.register(Bot)
admin.site.register(BotInstance)