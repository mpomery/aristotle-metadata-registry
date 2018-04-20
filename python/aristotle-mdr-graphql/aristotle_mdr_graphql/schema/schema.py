import graphene
from aristotle_mdr_graphql.schema.aristotle_mdr import Query as AristotleMDRQuery

# class BaseMeta:
#     model = mdr_models._concept
#     interfaces = (relay.Node, )
#     filter_fields = '__all__'

class AristotleQuery(AristotleMDRQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=AristotleQuery)
