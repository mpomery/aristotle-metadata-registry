import graphene
from aristotle_mdr_graphql.schema.aristotle_mdr import Query as AristotleMDRQuery
from aristotle_mdr_graphql.schema.aristotle_dse import Query as AristotleDSEQuery
from graphene_django.debug import DjangoDebug

class AristotleQuery(AristotleMDRQuery, AristotleDSEQuery, graphene.ObjectType):

    debug = graphene.Field(DjangoDebug, name='__debug')

schema = graphene.Schema(query=AristotleQuery)
