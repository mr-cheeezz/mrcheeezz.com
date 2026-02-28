from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.apps import apps
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse


included_apps = ['home', 'about', 'contact', 'projects', 'specs', 'bots', 'blog']

@user_passes_test(lambda u: u.is_staff)
def user_list(request):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]
    users = User.objects.all().order_by('-is_superuser', '-is_staff', 'username')
    context = {'active_page': 'admin:users','apps': False, 'app_names': app_names,'users': users}
    return render(request, 'admin/users/user-list.html', context)

@user_passes_test(lambda u: u.is_staff)
def edit_user(request, user_id):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]
    user = get_object_or_404(User, pk=user_id)
    if user.is_superuser and not request.user.is_superuser:
        return redirect('custom_admin:user_list')

    form = CustomUserChangeForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(reverse('custom_admin:user_list'))
    return render(request, 'admin/users/edit_user.html', {'active_page': 'admin:users','apps': False, 'app_names': app_names,'form': form, 'u': user})

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect(reverse('custom_admin:user_list'))
    return render(request, 'admin/users/delete_user.html', {'active_page': 'admin:users','apps': False, 'app_names': app_names,'u': user})

@user_passes_test(lambda u: u.is_superuser)
def add_user(request):
    app_names = [app.label for app in apps.get_app_configs() if app.label in included_apps]
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(reverse('custom_admin:user_list'))
    return render(request, 'admin/users/add_user.html', {'active_page': 'admin:users','apps': False, 'app_names': app_names,'form': form})
