"""
Aristotle MDR 11179 Link and Relationship models
================================================

These are based on the Slots definition in ISO/IEC 11179 Part 3 - 7.2.2.4
"""

from django.apps import apps
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf.global_settings import LANGUAGES
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible  # Python 2

from model_utils import Choices
from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR


class Relation(MDR.concept):  # 9.1.2.4
    """
    """
    arity = models.PositiveIntegerField(  # 9.1.2.4.3.1
        help_text=_('number of elements in the relation'),
        validators=[MinValueValidator(2)]
    )


class RelationRole(aristotleComponent):  # 9.1.2.5
    name = models.TextField(
        help_text=_("The primary name used for human identification purposes.")
    )
    definition = RichTextField(
        _('definition'),
        help_text=_("Representation of a concept by a descriptive statement "
                    "which serves to differentiate it from related concepts. (3.2.39)")
    )
    multiplicity = models.PositiveIntegerField(  # 9.1.2.5.3.1
        help_text=_(
            'number of links which must (logically) be members of the source '
            'relation of this role, differing only by an end with this role as '
            'an end_role.'
        ),
    )
    ordinal = models.PositiveIntegerField(  # 9.1.2.5.3.2
        help_text=_(
            'order of the relation role among other relation roles in the relation.'
        ),
        validators=[MinValueValidator(2)]
    )
    relation = models.ForeignKey(Relation)
    @property
    def parentItem(self):
        return self.conceptual_domain


class Link(TimeStampedModel):
    """
    Link is a class each instance of which models a link (3.2.69).
    A link is a member of a relation (3.2.119) (not an instance of a relation).
    In relational database parlance, a link would be a tuple (row) in a relation (table).
    Link is a subclass of Assertion (9.1.2.3), and as such is included in one or more
    Concept_Systems (9.1.2.2) through the assertion_inclusion (9.1.3.5) association.
    """
    arity = models.PositiveIntegerField(
        help_text=_('number of elements in the relation'),
        validators=[MinValueValidator(2)]
    )
    link_end_concept = models.ForeignKey(Relation)


class LinkEnd(TimeStampedModel):
    link = models.ForeignKey(Link, null=True)
    role = models.ForeignKey(RelationRole)
    concept = models.ForeignKey(MDR._concept, null=True)
