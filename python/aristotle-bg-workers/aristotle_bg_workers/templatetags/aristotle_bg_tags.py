from django import template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

register = template.Library()


@register.filter
def dejson(text):
    import json
    try:
        return json.loads(text)
    except:
        return text
