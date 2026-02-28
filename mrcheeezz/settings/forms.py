from django import forms
from .models import SiteSetting

class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['black_footer', 'home_title', 'active_upper', 'title_separator', 'typing_speed', 'theme', 'pfp_aura', 'game_links_enabled', 'blog_enabled']
        help_texts = {
            'black_footer': 'Enable/disable black color for the footer.',
            'home_title': 'Show "home" on hope page title',
            'active_upper': 'Enable/disable uppercase navbar name for active page.',
            'title_separator': 'Select the seperator',
            'typing_speed': 'Set the typing speed for typewrite effect on title for /.',
            'theme': 'Theme of site',
            'pfp_aura': 'Use "auto" to match profile picture color, or "none" to disable aura.',
            'game_links_enabled': 'Enable profile/game links on the game status card.',
            'blog_enabled': 'Enable/disable blog routes and blog links in navigation.',
    }
