from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.fields import DjangoConnectionField, DjangoListField
from graphene import Field
from aristotle_mdr import models as mdr_models
from django.db import models
import django_filters
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType


class ConceptNode(AristotleObjectType):

    class Meta:
        model = mdr_models._concept


class WorkgroupNode(AristotleObjectType):

    class Meta:
        model = mdr_models.Workgroup


class OrganizationNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Organization


class RegistrationAuthorityNode(AristotleObjectType):

    class Meta:
        model=mdr_models.RegistrationAuthority


# class DiscussionPostNode(AristotleObjectType):
#
#     class Meta:
#         model=mdr_models.DiscussionPost
#
#
# class DiscussionCommentNode(AristotleObjectType):
#
#     class Meta:
#         model=mdr_models.DiscussionComment'


class ReviewRequestNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ReviewRequest


class StatusNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Status


class ObjectClassNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ObjectClass


class PropertyNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Property


class MeasureNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Measure


class UnitOfMeasureNode(AristotleObjectType):

    class Meta:
        model=mdr_models.UnitOfMeasure


class DataTypeNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataType


class ConceptualDomainNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ConceptualDomain


class ValueMeaningNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ValueMeaning


class ValueDomainNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ValueDomain


class PermissibleValueNode(AristotleObjectType):

    class Meta:
        model=mdr_models.PermissibleValue


class SupplementaryValueNode(AristotleObjectType):

    class Meta:
        model=mdr_models.SupplementaryValue


class DataElementConceptNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataElementConcept


class DataElementNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataElement


class DataElementDerivationNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataElementDerivation


class Query(object):

    metadata = AristotleFilterConnectionField(ConceptNode)
    workgroups = AristotleFilterConnectionField(WorkgroupNode)
    organizations = AristotleFilterConnectionField(OrganizationNode)
    registration_authorities = AristotleFilterConnectionField(RegistrationAuthorityNode)
    #discussion_posts = AristotleFilterConnectionField(DiscussionPostNode)
    #discussion_comments = AristotleFilterConnectionField(DiscussionCommentNode)
    review_requests = AristotleFilterConnectionField(ReviewRequestNode)
    object_classes = AristotleFilterConnectionField(ObjectClassNode)
    properties = AristotleFilterConnectionField(PropertyNode)
    measures = AristotleFilterConnectionField(MeasureNode)
    unit_of_measures = AristotleFilterConnectionField(UnitOfMeasureNode)
    data_types = AristotleFilterConnectionField(DataTypeNode)
    conceptual_domains = AristotleFilterConnectionField(ConceptualDomainNode)
    value_domains = AristotleFilterConnectionField(ValueDomainNode)
    data_element_concepts = AristotleFilterConnectionField(DataElementConceptNode)
    data_elements = AristotleFilterConnectionField(DataElementNode)
    data_element_derivations = AristotleFilterConnectionField(DataElementDerivationNode)
