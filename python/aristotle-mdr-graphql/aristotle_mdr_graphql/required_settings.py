GRAPHENE_DEBUG = True

GRAPHENE = {
    'SCHEMA': 'aristotle_mdr_graphql.schema.schema',
}

if GRAPHENE_DEBUG:
    GRAPHENE['MIDDLEWARE'] = ['graphene_django.debug.DjangoDebugMiddleware']
