from django import template

register = template.Library()


@register.filter(name='get_by_key')
def get_by_key(dictionary, key):
    """Returns the value from a dictionary using a dynamic key."""
    return dictionary.get(key, "No Response")
