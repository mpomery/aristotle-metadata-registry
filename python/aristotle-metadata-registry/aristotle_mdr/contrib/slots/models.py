"""
Aristotle MDR 11179 Slots models
================================

These are based on the Slots definition in ISO/IEC 11179 Part 3 - 7.2.2.4
"""

from django.db import models

from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR
from aristotle_mdr.fields import ConceptForeignKey


class Slot(TimeStampedModel):
    # on save confirm the concept and model are correct, otherwise reject
    # on save confirm the cardinality
    name = models.CharField(max_length=256)  # Or some other sane length
    type = models.CharField(max_length=256, blank=True)  # Or some other sane length
    concept = ConceptForeignKey(MDR._concept, related_name='slots')
    value = models.TextField()
    order = models.PositiveSmallIntegerField("Position", default=0)
    permission = models.IntegerField(
        choices=(
            (0, 'Public'),
            (1, 'Authenticated'),
            (2, 'Workgroup'),
        ),
        default=0
    )

    def __str__(self):
        return u"{0} - {1}".format(self.name, self.value)

    class Meta:
        ordering = ['order']
