from django.contrib import admin
from .models import Social, Home

admin.site.register(Social)

@admin.register(Home)
class HomePageAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        if self.model.objects.count() > 0:
            return False
        return super().has_add_permission(request)