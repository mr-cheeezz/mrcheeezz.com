from django.contrib import admin

from .models import APICredential, SpotifyUser


@admin.register(APICredential)
class APICredentialAdmin(admin.ModelAdmin):
    list_display = ("provider", "client_id", "updated_at", "token_expiry")
    search_fields = ("provider",)
    readonly_fields = ("updated_at",)
    fieldsets = (
        ("Provider", {"fields": ("provider",)}),
        ("OAuth App", {"fields": ("client_id", "client_secret", "redirect_uri")}),
        ("Tokens", {"fields": ("access_token", "refresh_token", "token_expiry")}),
        ("Extra Config", {"fields": ("config", "updated_at")}),
    )


@admin.register(SpotifyUser)
class SpotifyUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "spotify_user_id", "token_expiry")
    search_fields = ("user_id", "spotify_user_id")
