#To access the field values dynamically, i create a custom template filter
from django import template

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    return getattr(obj, field_name, "")