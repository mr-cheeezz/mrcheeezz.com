from django.db.utils import OperationalError, ProgrammingError


def get_credential(provider):
    try:
        from .models import APICredential

        return APICredential.objects.filter(provider=provider).first()
    except (OperationalError, ProgrammingError):
        # During initial setup/migrations the table may not exist yet.
        return None


def get_provider_access_token(provider, fallback=""):
    credential = get_credential(provider)
    if credential and credential.access_token:
        return credential.access_token
    return fallback


def get_provider_refresh_token(provider, fallback=""):
    credential = get_credential(provider)
    if credential and credential.refresh_token:
        return credential.refresh_token
    return fallback


def get_provider_client_id(provider, fallback=""):
    credential = get_credential(provider)
    if credential and credential.client_id:
        return credential.client_id
    return fallback


def get_provider_client_secret(provider, fallback=""):
    credential = get_credential(provider)
    if credential and credential.client_secret:
        return credential.client_secret
    return fallback


def get_provider_redirect_uri(provider, fallback=""):
    credential = get_credential(provider)
    if credential and credential.redirect_uri:
        return credential.redirect_uri
    return fallback


def get_provider_config(provider, key, fallback=""):
    credential = get_credential(provider)
    if not credential or not isinstance(credential.config, dict):
        return fallback
    value = credential.config.get(key)
    if value in (None, ""):
        return fallback
    return value
