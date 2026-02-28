from django import template

register = template.Library()

@register.filter
def to_list(*args):
    return args
