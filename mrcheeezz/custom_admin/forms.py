from django import forms

class LogsPerPageForm(forms.Form):
  logs_per_page = forms.ChoiceField(choices=[(10, '10'), (25, '25'), (50, '50'), (100, '100')])
