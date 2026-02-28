from django import forms
from django.core.validators import URLValidator

from home.models import Social


PLATFORM_DOMAIN_MAP = {
    "discord.com": "discord",
    "discord.gg": "discord",
    "spotify.com": "spotify",
    "twitch.tv": "twitch",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "github.com": "github",
    "steamcommunity.com": "steam",
    "store.steampowered.com": "steam",
    "x.com": "twitter",
    "twitter.com": "twitter",
    "instagram.com": "instagram",
    "reddit.com": "reddit",
}


def _detect_platform(link):
    lower = link.lower()
    for domain, platform in PLATFORM_DOMAIN_MAP.items():
        if domain in lower:
            return platform
    return "website"


class SocialCreateForm(forms.Form):
    link = forms.CharField(
        label="Profile URL",
        max_length=255,
        validators=[URLValidator(schemes=["http", "https"])],
        help_text="Paste the full URL only. Icon/platform is auto-detected.",
    )

    def save(self):
        link = self.cleaned_data["link"].strip()
        platform = _detect_platform(link)
        max_order = Social.objects.order_by("-sort_order").values_list("sort_order", flat=True).first()
        sort_order = (max_order or 0) + 1
        return Social.objects.create(link=link, platform=platform, enabled=True, sort_order=sort_order)


class SocialEditForm(forms.ModelForm):
    link = forms.CharField(
        label="Profile URL",
        max_length=255,
        validators=[URLValidator(schemes=["http", "https"])],
    )

    class Meta:
        model = Social
        fields = ("platform", "link", "enabled", "sort_order")
        labels = {
            "platform": "Platform",
            "enabled": "Visible",
            "sort_order": "Order",
        }
