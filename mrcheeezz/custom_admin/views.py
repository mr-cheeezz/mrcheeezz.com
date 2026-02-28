from django.shortcuts import render, redirect
from django.apps import apps
from django.views import View
from django.contrib.admin.models import LogEntry
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from mrcheeezz.log import logger
from settings.models import SiteSetting
from settings.forms import SiteSettingForm
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from .forms import LogsPerPageForm
from django.urls import reverse
import subprocess

included_apps = ['home', 'about', 'contact', 'projects', 'specs', 'bots', 'blog']

def log_admin_action(request, view_name, app_name=None, model_name=None):
    if request.user.is_authenticated:
        user_info = f'User {request.user.username} accessed admin {view_name} view'
    else:
        user_info = 'User attempted to access admin panel'

    log_message = f'{user_info}'
    if app_name:
        log_message += f' for app {app_name}'
    if model_name:
        log_message += f', model {model_name}'

    logger.info(log_message)

@method_decorator(login_required, name='dispatch')
class Home(View):
    def get(self, request):
        if not request.user.is_staff:
            return redirect('home')
        app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]

        latest_logs = LogEntry.objects.all().order_by('-action_time')[:10]
        log_admin_action(request, 'home')
        return render(
            request,
            'admin/home.html',
            {'active_page': 'admin:home', 'apps': False, 'app_names': app_names, 'latest_logs': latest_logs},
        )

    def post(self, request):
        return redirect(reverse('custom_admin:home'))


@user_passes_test(lambda u: u.is_superuser)
def site_settings(request):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]
    settings = SiteSetting.objects.first()

    if request.method == 'POST':
        form = SiteSettingForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Site settings saved. You may need to restart the website service for some changes.",
            )
            return redirect(reverse('custom_admin:settings'))
    else:
        form = SiteSettingForm(instance=settings)

    return render(
        request,
        'admin/settings.html',
        {'active_page': 'admin:settings', 'apps': False, 'app_names': app_names, 'settings_form': form},
    )

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def restart_website(request):
    try:
        result = subprocess.run(
            ['systemctl', 'restart', 'website'],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return HttpResponse('Website restarted successfully.', content_type='text/plain')
        error_message = (result.stderr or result.stdout or '').strip() or f'command exited with {result.returncode}'
        return HttpResponse(f'Error restarting website: {error_message}', status=500, content_type='text/plain')
    except Exception as e:
        error_message = f'Error restarting website: {e}'
        return HttpResponse(error_message, status=500, content_type='text/plain')

@user_passes_test(lambda u: u.is_staff)
def logs(request):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]

    logs_per_page_form = LogsPerPageForm(request.GET)
    logs_per_page = int(request.GET.get('logs_per_page', 10))

    sort_by = request.GET.get('sort_by', 'action_time')
    sort_by_options = ['action_time', 'user']

    if sort_by not in sort_by_options:
        sort_by = 'action_time'

    current_year = datetime.now().year
    start_of_year = datetime(current_year, 1, 1)
    
    recent_actions = LogEntry.objects.filter(action_time__gte=start_of_year).order_by(f"-{sort_by}")

    paginator = Paginator(recent_actions, logs_per_page)
    page = request.GET.get('page')

    try:
        recent_actions = paginator.page(page)
    except PageNotAnInteger:
        return redirect(f"{reverse('custom_admin:logs')}?logs_per_page={logs_per_page}&page=1&sort_by={sort_by}")
    except EmptyPage:
        recent_actions = paginator.page(paginator.num_pages)

    return render(request, 'admin/logs.html', {
        'active_page': 'admin:logs',
        'apps': False,
        'app_names': app_names,
        'recent_actions': recent_actions,
        'logs_per_page_form': logs_per_page_form,
        'logs_per_page': logs_per_page,
        'options': [10, 25, 50, 100],
        'sort_by_options': sort_by_options,
        'selected_sort_by': sort_by,
    })
