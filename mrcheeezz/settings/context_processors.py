from .models import SiteSetting

def settings(request):
    settings = SiteSetting.objects.first()
    return {'settings': settings}
