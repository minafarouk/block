from django import template
import datetime
register = template.Library()

@register.filter(name='unix_to_datetime')
def unix_to_datetime(value):
    return datetime.datetime.fromtimestamp(int(value))