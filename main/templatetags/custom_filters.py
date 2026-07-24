import re
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''
    
@register.filter
def rub_to_kz(value):
    try:
        return int(value) * 6
    except (ValueError, TypeError):
        return ''
    
@register.filter
def unitycolor(value):
    pattern = r'<color=#([0-9A-Fa-f]{6})>(.*?)</color>'
    
    def repl(match):
        color = match.group(1)
        text = match.group(2)
        return f'<span style="color: #{color}">{text}</span>'

    return re.sub(pattern, repl, value)

@register.filter
def seconds_to_hours(value):
    return value // 3600