from .models import Home

def g(request):
    try:
        home_page = Home.objects.first()
    except Home.DoesNotExist:
        home_page = None

    return { 'g': home_page }