from django import template
register = template.Library()


@register.filter
def round_(val,place):
    if round(val,place) == int(val):
        return int(val)
    return round(val,place)