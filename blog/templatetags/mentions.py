from django import template
from django.template.defaultfilters import stringfilter
import re
from users.models import *
from django.core.exceptions import ObjectDoesNotExist
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


# @register.filter(name='mention', is_safe=True)
# @stringfilter
# def mention(value):
#     res = ""
#     my_list = value.split()
#     for i in my_list:
#         if i[0] == '@':
#             try:
#                 stng = i[:1]
#                 user = User.objects.get(username=stng)
#                 if user:
#                     profile_link = user
#                     i = f"<a href='{profile_link}/post/'>{i}</a>"
#
#             except ObjectDoesNotExist:
#                 print("Could not get the data")
#
#         res = res + i + ' '
#
#     return res
