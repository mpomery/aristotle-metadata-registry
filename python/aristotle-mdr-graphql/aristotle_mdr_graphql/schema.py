import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from aristotle_mdr import models as mdr_models

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

class Query(object):

    all_metadata = DjangoFilterConnectionField(ConceptNode)
    all_workgroups = DjangoFilterConnectionField(WorkgroupNode)

class AristotleQuery(Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=AristotleQuery)
