from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from mrcheeezz.views import redirect

from .models import Bot, BotInstance

class bots_list(TemplateView):
  template_name = 'bots/bot_types.html'

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args,**kwargs)
    context['bots'] = Bot.objects.all()
    context['active_page'] = 'bots'
    context['more'] = True

    return context
  
class bots_detail(TemplateView):
  template_name = 'bots/base.html'

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args,**kwargs)
    bot = get_object_or_404(Bot, slug=self.kwargs['name'])
    context['bot'] = bot
    context['active_page'] = 'bots'
    context['out_message'] = 'this bot is no longer in use'
    context['more'] = True

    return context

def bot_redirect(request, bot, streamer):
    bot = get_object_or_404(Bot, bot=bot)
    bot_instance = get_object_or_404(BotInstance, bot=bot, streamer=streamer)
    website_url = bot_instance.website
    
    return redirect(request, message=f'Redirecting to bot website for {streamer}', e_url=website_url)