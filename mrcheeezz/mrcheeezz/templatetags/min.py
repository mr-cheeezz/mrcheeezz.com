from django import template
from django.conf import settings
import rjsmin
import rcssmin

register = template.Library()

@register.filter
def min_js(js_code):
  if getattr(settings, 'HTML_MINIFY', False):
    return rjsmin.jsmin(js_code)
  return js_code

@register.filter
def min_css(css_code):
  if getattr(settings, 'HTML_MINIFY', False):
    return rcssmin.cssmin(css_code)
  return css_code