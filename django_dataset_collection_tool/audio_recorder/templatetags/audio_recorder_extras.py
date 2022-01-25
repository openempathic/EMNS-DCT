from atexit import register
from django import template

register = template.Library()

@register.simple_tag
def filtered_paginated_url(value, field_name, urlencode=None):
    url = f'?{field_name}={value}'
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0]!=field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = f'{url}&{encoded_querystring}'
    return url