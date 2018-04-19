import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from aristotle_mdr import models as mdr_models

# class BaseMeta:
#     model = mdr_models._concept
#     interfaces = (relay.Node, )
#     filter_fields = '__all__'


class ConceptNode(DjangoObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = '__all__'


class WorkgroupNode(DjangoObjectType):

    class Meta:
        model = mdr_models.Workgroup
        interfaces = (relay.Node, )
        filter_fields = '__all__'


class OrganizationNode(DjangoObjectType):

    class Meta:
        model=mdr_models.Organization
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class RegistrationAuthorityNode(DjangoObjectType):

    class Meta:
        model=mdr_models.RegistrationAuthority
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DiscussionPostNode(DjangoObjectType):

    class Meta:
        model=mdr_models.DiscussionPost
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DiscussionCommentNode(DjangoObjectType):

    class Meta:
        model=mdr_models.DiscussionComment
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ReviewRequestNode(DjangoObjectType):

    class Meta:
        model=mdr_models.ReviewRequest
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class StatusNode(DjangoObjectType):

    class Meta:
        model=mdr_models.Status
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ObjectClassNode(DjangoObjectType):

    class Meta:
        model=mdr_models.ObjectClass
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class PropertyNode(DjangoObjectType):

    class Meta:
        model=mdr_models.Property
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class MeasureNode(DjangoObjectType):

    class Meta:
        model=mdr_models.Measure
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class UnitOfMeasureNode(DjangoObjectType):

    class Meta:
        model=mdr_models.UnitOfMeasure
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataTypeNode(DjangoObjectType):

    class Meta:
        model=mdr_models.DataType
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ConceptualDomainNode(DjangoObjectType):

    class Meta:
        model=mdr_models.ConceptualDomain
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ValueMeaningNode(DjangoObjectType):

    class Meta:
        model=mdr_models.ValueMeaning
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class ValueDomainNode(DjangoObjectType):

    class Meta:
        model=mdr_models.ValueDomain
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class PermissibleValueNode(DjangoObjectType):

    class Meta:
        model=mdr_models.PermissibleValue
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class SupplementaryValueNode(DjangoObjectType):

    class Meta:
        model=mdr_models.SupplementaryValue
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataElementConceptNode(DjangoObjectType):

    class Meta:
        model=mdr_models.DataElementConcept
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataElementNode(DjangoObjectType):

    class Meta:
        model=mdr_models.DataElement
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class DataElementDerivationNode(DjangoObjectType):

    class Meta:
        model=mdr_models.DataElementDerivation
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class Query(object):

    metadata = DjangoFilterConnectionField(ConceptNode)
    #metadata = relay.Node.Field(ConceptNode)
    workgroups = DjangoFilterConnectionField(WorkgroupNode)

class AristotleQuery(Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=AristotleQuery)
