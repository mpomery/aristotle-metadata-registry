from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _
from model_utils import Choices

from aristotle_mdr.models import RichTextField
import aristotle_mdr as aristotle
from aristotle_mdr.fields import ConceptForeignKey, ConceptManyToManyField


class IndicatorType(aristotle.models.concept):
    pass

# Subclassing from DataElement causes indicators to present as DataElements, which isn't quite right.
class Indicator(aristotle.models.concept):
    """
    An indicator is a single measure that is reported on regularly
    and that provides relevant and actionable information about population or system performance.
    """
    template = "comet/indicator.html"
    dataElementConcept = ConceptForeignKey(
        aristotle.models.DataElementConcept,
        verbose_name = "Data Element Concept",
        blank=True,
        null=True
    )
    valueDomain = ConceptForeignKey(
        aristotle.models.ValueDomain,
        verbose_name = "Value Domain",
        blank=True,
        null=True
    )
    outcome_areas = ConceptManyToManyField('OutcomeArea',related_name="indicators",blank=True)

    indicatorType = ConceptForeignKey(IndicatorType, blank=True, null=True)
    numerators = ConceptManyToManyField(
        aristotle.models.DataElement,
        related_name="as_numerator",
        blank=True
    )
    denominators = ConceptManyToManyField(
        aristotle.models.DataElement,
        related_name="as_denominator",
        blank=True
    )
    disaggregators = ConceptManyToManyField(
        aristotle.models.DataElement,
        related_name="as_disaggregator",
        blank=True
    )

    numerator_description = models.TextField(blank=True)
    numerator_computation = models.TextField(blank=True)
    denominator_description = models.TextField(blank=True)
    denominator_computation = models.TextField(blank=True)
    computationDescription = RichTextField(blank=True)
    rationale = RichTextField(blank=True)
    disaggregation_description = RichTextField(blank=True)

class IndicatorSetType(aristotle.models.unmanagedObject):
    pass

class IndicatorSet(aristotle.models.concept):
    template = "comet/indicatorset.html"
    indicators = ConceptManyToManyField(Indicator,related_name="indicatorSets",blank=True,null=True)
    indicatorSetType = models.ForeignKey(IndicatorSetType,blank=True,null=True)

class OutcomeArea(aristotle.models.concept):
    template = "comet/outcomearea.html"

class QualityStatement(aristotle.models.concept):
    template = "comet/qualitystatement.html"
    timeliness  = RichTextField(blank=True)
    accessibility  = RichTextField(blank=True)
    interpretability  = RichTextField(blank=True)
    relevance  = RichTextField(blank=True)
    accuracy  = RichTextField(blank=True)
    coherence  = RichTextField(blank=True)
    implementationStartDate = models.DateField(blank=True,null=True)
    implementationEndDate = models.DateField(blank=True,null=True)

class Framework(aristotle.models.concept):
    template = "comet/framework.html"
    parentFramework = ConceptForeignKey('Framework',blank=True,null=True,related_name="childFrameworks")
    indicators = ConceptManyToManyField(Indicator,related_name="frameworks",blank=True)

# def defaultData():
#     print("Add aristotle defaults")
#     aristotle.models.defaultData()
#     indicatorTypes = [
#       ("Indicator",""),
#       ("Output measure",""),
#       ("Progress measure",""),
#       ]
#     print("Adding indicator types")
#     for name,desc in indicatorTypes:
#         it,created = IndicatorType.objects.get_or_create(name=name,definition=desc)
#     indicatorSetTypes = [
#       ("COAG-IGA","This includes indicators outlined in the Council of Australian government (COAG) Intergovernmental Agreement (IGA) on Federal Financial Relations relevant to national reporting on health, housing assistance and community services. The overall objective of these agreements is the improvement of the well-being of all Australians."),
#       ("COAG-NP","The Council of Australian Governments (COAG) has agreed to a new form of payment called National Partnership (NP) payments to fund specific projects and to facilitate and/or reward States that deliver on nationally-significant reforms."),
#       ("ROGS","The Review of Government Service Provision was established in 1993 by Heads of government (now the Council of Australian Governments or COAG) to provide information on the effectiveness and efficiency of government services in Australia. A Steering Committee, comprising senior representatives from the central agencies of all governments, manages the Review with the assistance of a Secretariat provided by the Productivity Commission."),
#       ]
#     print("Adding indicator set types")
#     for name,desc in indicatorSetTypes:
#         ist,created = IndicatorSetType.objects.get_or_create(name=name,definition=desc)
