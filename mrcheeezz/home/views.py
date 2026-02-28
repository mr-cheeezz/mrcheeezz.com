from django.views import View
from django.shortcuts import render

from .models import Social

from website.info import Responses

from mrcheeezz import env

class Home(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        context = {
            'social': Social.objects.filter(enabled=True).order_by('sort_order', 'title'),
            'size': env.svg_size,
            'typewrite': Responses,
            'active_page': 'home',
            'more': False,
            'home': True,
        }
        return render(request, self.template_name, context)
