from django import forms
from .models import About, Settings


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = (
            "use",
            "show_location",
            "country",
            "state",
            "city",
            "show_age",
            "birth_year",
            "birth_month",
            "birth_day",
            "programming_start",
            "programming_languages",
        )
        labels = {
            "use": "Enable About Page",
            "show_location": "Show Location",
            "show_age": "Show Age",
        }


class AboutSectionForm(forms.ModelForm):
    class Meta:
        model = About
        fields = ("title", "content")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Section title (Markdown supported)",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": "Write your section in Markdown...",
                }
            ),
        }
