from django.conf.urls import url

urlpatterns = [
    url(r'^graphql', GraphQLView.as_view(graphiql=True, schema=schema))
]
