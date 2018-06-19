from django.views.generic import ListView

from aristotle_mdr.models import _concept
from aristotle_mdr.contrib.slots.models import Slot
from aristotle_mdr.contrib.slots.utils import concepts_with_similar_slots


class SimilarSlotsView(ListView):
    template_name = "aristotle_mdr/slots/similar_slots_list.html"
    model = _concept

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'slot_name': self.kwargs['slot_name']})
        context.update({'value': self.request.GET.get('value', None)})
        return context

    def get_queryset(self, *args, **kwargs):
        value = self.request.GET.get('value', None)
        return concepts_with_similar_slots(
            self.request.user, self.kwargs['slot_name'], value=value
        ).all()
