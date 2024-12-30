from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get dictionary item by key
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def get_file_name(file_dict):
    """
    Template filter to get file name from session storage
    Usage: {{ file_dict|get_file_name }}
    """
    return file_dict.get('name', '') if file_dict else ''