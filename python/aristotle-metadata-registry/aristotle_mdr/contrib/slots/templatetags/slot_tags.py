from django import template

from aristotle_mdr.contrib.slots.models import Slot
from aristotle_mdr.contrib.slots.utils import concepts_with_similar_slots


register = template.Library()


@register.simple_tag
def count_similar(user, slot):
    return concepts_with_similar_slots(user, slot=slot).count()


@register.filter
def slots_by_type(concept, name):
    return concept.slots.filter(name=name, permission=0)
