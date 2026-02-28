from markdown import markdown
from django.shortcuts import render
from mrcheeezz.views import redirect
from .models import About, Settings
from .forms import AboutSectionForm, SettingsForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory
from website.info import *


class about(TemplateView):
  template_name = 'about.html'

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args,**kwargs)

    about_list = About.objects.all()
    abouts = []

    for about in about_list:
      html_title = markdown(about.title)
      html_content = markdown(about.content)
      abouts.append({
        'title': html_title,
        'content': html_content
      })

    settings, _ = Settings.objects.get_or_create(pk=1)

    context['timezone'] = TimeZone
    context['welcome'] = WelcomeMsg
    context['meta'] = settings.to_dict()
    context['ex_content'] = abouts
    context['active_page'] = 'about'
    context['more'] = False

    return context
  
@user_passes_test(lambda u: u.is_superuser)
def about_settings(request):
    global_settings, _ = Settings.objects.get_or_create(pk=1)
    AboutFormSet = modelformset_factory(
        About,
        form=AboutSectionForm,
        extra=1,
        can_delete=True,
    )

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=global_settings)
        formset = AboutFormSet(request.POST, queryset=About.objects.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect(request, message='Succsuffly saved settings', e_url='/about')
    else:
        form = SettingsForm(instance=global_settings)
        formset = AboutFormSet(queryset=About.objects.all())

    context = {
        'about': global_settings.to_dict(),
        'form': form,
        'formset': formset,
    }

    return render(request, 'about/settings.html', context)
