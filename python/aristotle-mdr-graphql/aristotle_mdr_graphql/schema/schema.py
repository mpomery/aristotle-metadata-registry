import graphene
from aristotle_mdr_graphql.schema.aristotle_mdr import Query as AristotleMDRQuery
from aristotle_mdr_graphql.schema.aristotle_dse import Query as AristotleDSEQuery
from aristotle_mdr_graphql.schema.comet import Query as CometQuery
from graphene_django.debug import DjangoDebug

class AristotleQuery(CometQuery, AristotleDSEQuery, AristotleMDRQuery, graphene.ObjectType):
    "The query root of the Aristotle GraphQL API"
    pass
#     #debug = graphene.Field(DjangoDebug, name='__debug')

# class AristotleQuery(AristotleMDRQuery, AristotleDSEQuery, graphene.ObjectType):
    # "The query root of the Aristotle GraphQL API"
    # pass
    #debug = graphene.Field(DjangoDebug, name='__debug')

schema = graphene.Schema(query=AristotleQuery)
