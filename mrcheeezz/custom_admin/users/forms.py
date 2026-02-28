from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class BanUserForm(forms.Form):
    BAN_REASONS = [
        ('violation', 'Violation of Community Guidelines'),
        ('spamming', 'Spamming'),
        ('harassment', 'Harassment or Bullying'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('impersonation', 'Impersonation'),
        ('multiple_accounts', 'Multiple Account Violation'),
        ('hate_speech', 'Hate Speech or Discrimination'),
        ('security_violation', 'Security Violation'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('other', 'Other (Specify Below)'),
    ]

    ban_reason = forms.ChoiceField(choices=BAN_REASONS, widget=forms.Select(attrs={'class': 'form-control'}))
    mod_note = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))

class PasswordChangeButtonWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return f'<a href="/accounts/settings/change-password" class="password-change-button">Change Password</a>'

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'user_permissions')
        labels = {
            'is_staff': 'Moderator',
            'is_superuser': 'Administrator',
        }

        CATEGORY_HEADERS = {
            'username': 'Credentials',
            'first_name': 'Personal Information',
            'is_staff': 'Permissions',
        }

        CAT_BREAKS = {
            'password2': True,
            'email': True,
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = False
        self.fields['last_name'].required = False

        for field_name in self.fields:
            field_meta = self.fields[field_name].widget.attrs.get('meta', {})
            field_meta['category'] = self.Meta.CATEGORY_HEADERS.get(field_name, None)
            field_meta['break'] = self.Meta.CAT_BREAKS.get(field_name, False)
            self.fields[field_name].widget.attrs['meta'] = field_meta

class CustomUserChangeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        widgets = {
            'password': PasswordChangeButtonWidget(),
        }
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'user_permissions')
        labels = {
            'is_staff': 'Moderator',
            'is_superuser': 'Administrator',
        }

        CATEGORY_HEADERS = {
            'username': 'Credentials',
            'first_name': 'Personal Information',
            'is_staff': 'Permissions',
            'last_login': 'Important Dates'
        }

        CAT_BREAKS = {
            'password': True,
            'email': True,
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field_meta = self.fields[field_name].widget.attrs.get('meta', {})
            field_meta['category'] = self.Meta.CATEGORY_HEADERS.get(field_name, None)
            field_meta['break'] = self.Meta.CAT_BREAKS.get(field_name, False)
            self.fields[field_name].widget.attrs['meta'] = field_meta
