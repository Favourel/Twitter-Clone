from django import template
from django.template.defaultfilters import stringfilter
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='mentions', is_safe=True)
@stringfilter
def mentions(value):
    value = re.sub(r'@(\w+)', r'<a href="/\1/post">@\1</a>', value)
    return value


@register.filter(name='hashtags', is_safe=True)
@stringfilter
def hashtags(value):
    value = re.sub(r'#(\w+)', r'<a href="/search/?q=\1&submit=Search">#\1</a>', value)
    return value


@register.filter
def highlight_search(text, search):
    highlighted = text.replace(search, '<b><em>{}</em></b>'.format(search))
    return mark_safe(highlighted)


