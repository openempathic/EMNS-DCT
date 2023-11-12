from django import template
import re

register = template.Library()

YOUTUBE_ID_REGEX = re.compile(r'youtube\.com/embed/([^?]+)')
YOUTUBE_START_REGEX = re.compile(r'start=([^&]+)')
YOUTUBE_END_REGEX = re.compile(r'end=([^&]+)')

@register.filter
def youtube_id(url):
    match = YOUTUBE_ID_REGEX.search(url)
    return match.group(1) if match else ''

@register.filter
def youtube_start(url):
    match = YOUTUBE_START_REGEX.search(url)
    return match.group(1) if match else '0'

@register.filter
def youtube_end(url):
    match = YOUTUBE_END_REGEX.search(url)
    return match.group(1) if match else '0'
