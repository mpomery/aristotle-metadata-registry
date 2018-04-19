from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django import DjangoFilterConnectionField

from aristotle_mdr import models as mdr_models

class ConecptNode(DjangoObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )

class Query(object):

    all_metadata = DjangoFilterConnectionField(ContentType)
