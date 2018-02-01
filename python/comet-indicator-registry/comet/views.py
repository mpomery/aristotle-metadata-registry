import aristotle_mdr as aristotle
from aristotle_mdr.contrib.generic.views import GenericAlterManyToManyView
import comet
from django.views.generic import TemplateView

class DynamicTemplateView(TemplateView):
    def get_template_names(self):
        return ['comet/static/%s.html' % self.kwargs['template']]

class OutcomeAlterIndicators(GenericAlterManyToManyView):
    model_base = comet.models.OutcomeArea
    model_to_add = comet.models.Indicator
    model_base_field = 'indicators'
