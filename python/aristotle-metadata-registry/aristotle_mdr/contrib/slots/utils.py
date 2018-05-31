from aristotle_mdr.contrib.slots.models import Slot

def get_allowed_slots(concept, user):

    slots = Slot.objects.filter(concept=concept)

    # If slots is empty no need for further filtering
    if not slots:
        return slots

    if user.is_authenticated:
        if concept.workgroup in user.profile.workgroups:
            # return all slots
            return slots
        else:
            # Return public and auth only slots
            return slots.filter(permission__in=[0, 1])
    else:
        # Only return public slots
        return slots.filter(permission=0)
