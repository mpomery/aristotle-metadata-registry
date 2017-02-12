from django import template
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

from aristotle_mdr.contrib.links.models import Link

register = template.Library()

@register.filter
def get_links(item):
    return Link.objects.filter(linkend__concept=item).all().distinct()
