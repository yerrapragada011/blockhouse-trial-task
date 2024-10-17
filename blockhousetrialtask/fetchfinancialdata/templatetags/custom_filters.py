import base64
from django import template

register = template.Library()

@register.filter
def b64encode(value):
    if isinstance(value, bytes):
        return base64.b64encode(value).decode('utf-8')
    elif hasattr(value, 'getvalue'):
        return base64.b64encode(value.getvalue()).decode('utf-8')
    else:
        raise TypeError("Expected bytes or BytesIO object for base64 encoding")
