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

import logging
logger = logging.getLogger(__name__)

class ConceptNode(AristotleObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = '__all__'


class WorkgroupNode(AristotleObjectType):

    class Meta:
        model = mdr_models.Workgroup
        interfaces = (relay.Node, )
        filter_fields = '__all__'


class OrganizationNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Organization
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class RegistrationAuthorityNode(AristotleObjectType):

    class Meta:
        model=mdr_models.RegistrationAuthority
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


# class DiscussionPostNode(AristotleObjectType):
#
#     class Meta:
#         model=mdr_models.DiscussionPost
#         interfaces=interfaces = (relay.Node, )
#         filter_fields = '__all__'
#
#
# class DiscussionCommentNode(AristotleObjectType):
#
#     class Meta:
#         model=mdr_models.DiscussionComment
#         interfaces=interfaces = (relay.Node, )
#         filter_fields = '__all__'


class ReviewRequestNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ReviewRequest
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class StatusNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Status
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ObjectClassNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ObjectClass
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class PropertyNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Property
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class MeasureNode(AristotleObjectType):

    class Meta:
        model=mdr_models.Measure
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class UnitOfMeasureNode(AristotleObjectType):

    class Meta:
        model=mdr_models.UnitOfMeasure
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataTypeNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataType
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ConceptualDomainNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ConceptualDomain
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ValueMeaningNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ValueMeaning
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ValueDomainNode(AristotleObjectType):

    class Meta:
        model=mdr_models.ValueDomain
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class PermissibleValueNode(AristotleObjectType):

    class Meta:
        model=mdr_models.PermissibleValue
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class SupplementaryValueNode(AristotleObjectType):

    class Meta:
        model=mdr_models.SupplementaryValue
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataElementConceptNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataElementConcept
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataElementNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataElement
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataElementDerivationNode(AristotleObjectType):

    class Meta:
        model=mdr_models.DataElementDerivation
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


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
