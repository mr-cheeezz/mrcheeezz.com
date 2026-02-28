from django.apps import apps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from home.models import Social

from .forms import SocialCreateForm, SocialEditForm


included_apps = ['home', 'about', 'contact', 'projects', 'specs', 'bots', 'blog']


@user_passes_test(lambda u: u.is_superuser)
def socials_home(request):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]
    socials = Social.objects.all().order_by('sort_order', 'title')

    if request.method == 'POST':
        form = SocialCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('custom_admin:socials_home'))
    else:
        form = SocialCreateForm()

    return render(
        request,
        'admin/socials/home.html',
        {
            'active_page': 'admin:socials',
            'apps': False,
            'app_names': app_names,
            'socials': socials,
            'form': form,
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def edit_social(request, social_id):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]
    social = get_object_or_404(Social, pk=social_id)

    form = SocialEditForm(request.POST or None, instance=social)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(reverse('custom_admin:socials_home'))

    return render(
        request,
        'admin/socials/edit.html',
        {
            'active_page': 'admin:socials',
            'apps': False,
            'app_names': app_names,
            'form': form,
            'social': social,
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def delete_social(request, social_id):
    social = get_object_or_404(Social, pk=social_id)
    if request.method == 'POST':
        social.delete()
        return redirect(reverse('custom_admin:socials_home'))

    return redirect(reverse('custom_admin:socials_home'))
