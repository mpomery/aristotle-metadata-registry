from django.conf.urls import url
from graphene_django.views import GraphQLView
from aristotle_mdr_graphql.schema.schema import schema
from aristotle_mdr_graphql.views import FancyGraphQLView
from django.views.generic import TemplateView
from textwrap import dedent

urlpatterns = [
    url(r'^/?$', TemplateView.as_view(template_name="aristotle_mdr_graphql/explorer.html"), name='graphql_explorer'),
    url(r'^api', FancyGraphQLView.as_view(
        graphiql=True,
        schema=schema,
        default_query=dedent("""
            # This query fetches the name of the first 5 metadata items you
            # have permission to see
            # Use the documentation on the right to build futher queries
            
            query {
              metadata (first: 5) {
                edges {
                  node {
                    name
                    definition
                  }
                }
              }
            }
            """)
    ), name='graphql_api'),
]
