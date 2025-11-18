from django import template

register = template.Library()

@register.filter
def split_first(value, separator=','):
    if value:
        return str(value).split(separator)[0]
    return value
