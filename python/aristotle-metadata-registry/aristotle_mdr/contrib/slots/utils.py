from aristotle_mdr.contrib.slots.models import Slot
from aristotle_mdr import models as MDR


def filter_slot_perms(slots, user, workgroup=None):

    # If slots is empty no need for further filtering
    if not slots:
        return slots

    if user.is_authenticated:
        if workgroup in user.profile.workgroups:
            # return all slots
            return slots
        else:
            # Return public and auth only slots
            return slots.filter(permission__in=[0, 1])
    else:
        # Only return public slots
        return slots.filter(permission=0)


def get_allowed_slots(concept, user):

    slots = Slot.objects.filter(concept=concept)
    return filter_slot_perms(slots, user, concept.workgroup)


def concepts_with_similar_slots(user, name=None, _type=None, value=None, slot=None):
    if not (slot is not None or _type is not None or name is not None):
        return MDR._concept.objects.none()

    if slot is not None:
        name = slot.name
        _type = slot.type
        value = slot.value

    slots = MDR._concept.objects.visible(user)

    if name:
        slots = slots.filter(slots__name=name, slots__permission=0)

    if _type:
        slots = slots.filter(slots__type=_type, slots__permission=0)

    if value:
        slots = slots.filter(slots__value=value, slots__permission=0)

    if slot:
        slots = slots.exclude(id=slot.concept.id)

    return slots.distinct()
