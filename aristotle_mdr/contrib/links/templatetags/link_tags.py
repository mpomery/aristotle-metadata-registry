from django import template

from aristotle_mdr.contrib.links.models import Link
from aristotle_mdr.contrib.links import perms

register = template.Library()


@register.filter
def get_links(item):
    return Link.objects.filter(linkend__concept=item).all().distinct()


@register.filter
def can_edit_link(user, link):
    return perms.user_can_change_link(user, link)
