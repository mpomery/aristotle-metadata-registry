import graphene
from aristotle_mdr_graphql.schema.aristotle_mdr import Query as AristotleMDRQuery
from aristotle_mdr_graphql.schema.aristotle_dse import Query as AristotleDSEQuery
from aristotle_mdr_graphql.schema.comet import Query as CometQuery
from graphene_django.debug import DjangoDebug

class AristotleQuery(AristotleMDRQuery, AristotleDSEQuery, CometQuery, graphene.ObjectType):

    debug = graphene.Field(DjangoDebug, name='__debug')

schema = graphene.Schema(query=AristotleQuery)
