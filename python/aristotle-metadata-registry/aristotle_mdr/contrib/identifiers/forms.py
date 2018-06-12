from django.forms.models import inlineformset_factory
from django.forms.widgets import HiddenInput
from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier


def identifier_inlineformset_factory():

    return inlineformset_factory(
        MDR._concept, ScopedIdentifier,
        can_delete=True,
        fields=('concept', 'namespace', 'identifier', 'version', 'order'),
        extra=0,
        widgets={'order': HiddenInput()}
    )
