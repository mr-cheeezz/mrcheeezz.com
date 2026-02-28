from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden


class StorePreviousURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/static') and not request.path.startswith('/error'):
            request.session['previous_url'] = request.path
        response = self.get_response(request)
        return response
    
class BannedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.user.is_banned and not request.path.startswith('/not-approved'):
            return redirect('/not-approved')

        return response
    
class NotAllowedAdmin:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path.startswith(settings.ADMIN_URL):
            request.custom_admin_access_forbidden = True
            return HttpResponseForbidden()

        response = self.get_response(request)
        return response
    
class UnauthorizedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, 'user', None)

        if user and not (user.is_superuser or user.is_staff) and request.path.startswith('/admin/'):
            context = {
                'error_code': 401,
                'error_message': 'Unauthorized Access',
                'extra_message': "You don't have access to this page.",
            }
            return render(request, 'error.html', context, status=401)

        return response