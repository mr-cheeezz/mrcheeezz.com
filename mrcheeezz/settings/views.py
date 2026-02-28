from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import SiteSetting
from .forms import SiteSettingForm

@method_decorator(login_required, name='dispatch')
class Settings(View):
    def get(self, request):
        if not request.user.is_superuser:
            return redirect('home')
        settings = SiteSetting.objects.first()
        form = SiteSettingForm(instance=settings)
        return render(request, 'settings/config.html', {'settings': settings, 'form': form})

    def post(self, request):
        if not request.user.is_superuser:
            return redirect('home')
        settings = SiteSetting.objects.first()
        form = SiteSettingForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
        return redirect('settings')