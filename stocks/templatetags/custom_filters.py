from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    val = dictionary.get(key, '')
    if type(val) == float:
        val = round(val,2)
    return val

@register.filter
def round_(val,place):
    if round(val,place) == int(val):
        return int(val)
    return round(val,place)

@register.filter
def value_index(List, i):
    return List[int(i)]
