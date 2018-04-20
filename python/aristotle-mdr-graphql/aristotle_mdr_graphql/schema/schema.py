import graphene
from aristotle_mdr_graphql.schema.aristotle_mdr import Query as AristotleMDRQuery

class AristotleQuery(AristotleMDRQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=AristotleQuery)
