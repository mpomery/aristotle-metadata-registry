from graphene_django.views import GraphQLView
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

import logging
logger = logging.getLogger(__name__)

class FancyGraphQLView(GraphQLView):
    default_query = ""

    def __init__(self, *args, **kwargs):
        self.default_query = kwargs.pop("default_query", "")
        super().__init__(*args, **kwargs)

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        if 'html' in request.content_type or not request.content_type:
            if "noexplorer" not in request.GET.keys() and "raw" not in request.GET.keys():
                return redirect("aristotle_graphql:graphql_explorer")
        return super().dispatch(request, *args, **kwargs)

    def render_graphiql(self, request, **data):
        # If there is no query we want to render something useful
        data['query'] = data.get("query") or self.default_query
        return render(request, self.graphiql_template, data)
