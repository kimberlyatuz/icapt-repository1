# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

#to get submission.data dynamically


@register.filter
def get(value, key):
    return value.get(key, '')

@register.filter
def get_field_value(instance, field_name):
    """Retrieve the value of a model field dynamically."""
    return getattr(instance, field_name)

@register.simple_tag
def get_field_names(model):
    """Return a list of field names for a given model."""
    return [field.name for field in model._meta.fields]

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def get_field_value(submission, field_name):
    """Retrieve the value of a model field dynamically, with error handling."""
    print(f"Getting field value for: {field_name}")  # Debug output
    try:
        return getattr(submission, field_name)
    except AttributeError:
        return 'Field not found'