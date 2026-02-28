from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from ..env import google_analytics as GACODE

register = template.Library()

@register.filter
@stringfilter
def title_if_lowercase(value):
  if value.islower():
    return value.title()
  else:
    return value

@register.filter
@stringfilter
def remove_last(value):
  return value[:-1]

@register.filter
def is_odd(value):
  return value % 2 != 0

@register.filter
def is_even(value):
    return value % 2 == 0

@register.tag(name="google_analytics")
def do_google_analytics(parser, token):
  nodelist = parser.parse(('endgoogle_analytics',))
  parser.delete_first_token()
  return GoogleAnalyticsNode(nodelist)

class GoogleAnalyticsNode(template.Node):
  def __init__(self, nodelist):
    self.nodelist = nodelist

  def render(self, context):
    if getattr(settings, 'HTML_MINIFY', False):
      content = "window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{}');".format(GACODE)
      return "<script>{}</script>".format(content)
    else:
      return """
      <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{}');
      </script>
      """.format(GACODE)
    
@register.filter
def get_model_name(model):
  return model._meta.model_name

@register.filter
def get_verbose_name_plural(model):
  return model._meta.verbose_name_plural

@register.filter(name='class_name')
def class_name(value):
  return value.__class__.__name__

@register.filter(name='format_change_message')
def format_change_message(change_message):
  cleaned_message = re.sub(r'[{}()\[\]":]', '', change_message)
  return mark_safe(cleaned_message)

@register.filter(name='underscore_to_space')
def underscore_to_space(value):
    return value.replace('_', ' ')

@register.filter(name='is_na')
def is_na(value):
  if not value or set(value) <= {'{', '}', '[', ']', '(', ')'}:
    return 'N/A'
  return value


@register.filter(name='versioned_asset_path')
@stringfilter
def versioned_asset_path(value):
  """
  Convert '/static/gen/scripts/bundle.js?12345' into
  '/static/gen/scripts/bundle.12345.js'.
  Falls back to original value if no query version is present.
  """
  try:
    parsed = urlsplit(value)
    if not parsed.query:
      static_url = getattr(settings, "STATIC_URL", "/static/")
      if parsed.path.startswith(static_url):
        rel = parsed.path[len(static_url):].lstrip("/")
        fs_path = Path(settings.PROJECT_ROOT) / "static" / rel
        if fs_path.exists() and fs_path.is_file():
          version = str(int(fs_path.stat().st_mtime))
          base, ext = parsed.path.rsplit(".", 1)
          return f"{base}.{version}.{ext}"
      return value

    query = parsed.query.strip()
    version = None
    if query.isdigit():
      version = query
    else:
      q = parse_qs(query)
      for key in ("v", "version"):
        if q.get(key):
          version = q[key][0]
          break
      if not version and len(q) == 1:
        version = next(iter(q.values()))[0]

    if not version:
      return value

    path = parsed.path
    if "." not in path.rsplit("/", 1)[-1]:
      return value
    base, ext = path.rsplit(".", 1)
    return f"{base}.{version}.{ext}"
  except Exception:
    return value
