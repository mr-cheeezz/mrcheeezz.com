from django import template

register = template.Library()

@register.filter
def slice_words(value, arg):
  words = value.split()[:arg]
  return ' '.join(words)