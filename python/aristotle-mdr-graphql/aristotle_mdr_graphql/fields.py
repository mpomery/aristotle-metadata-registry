from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.fields import DjangoConnectionField
from graphene_django.utils import maybe_queryset
from django.db import models
import django_filters

from aristotle_mdr_graphql.filterset import (AristotleFilterSet,
                                             ConceptFilterSet)


class AristotleFilterConnectionField(DjangoFilterConnectionField):
    def __init__(self, type, *args, **kwargs):

        extrameta = {
            'filterset_base_class': AristotleFilterSet
        }

        kwargs.update({'extra_filter_meta': extrameta})
        super().__init__(type, *args, **kwargs)

    @classmethod
    def connection_resolver(cls, resolver, connection, default_manager, max_limit,
                            enforce_first_or_last, filterset_class, filtering_args,
                            root, info, **args):

        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        qs = filterset_class(
            data=filter_kwargs,
            queryset=default_manager.get_queryset(),
            request=info.context
        ).qs

        qs = qs.visible(info.context.user) # Top level filtering to only visible objects

        return super(DjangoFilterConnectionField, cls).connection_resolver(
            resolver,
            connection,
            qs,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **args
        )


class AristotleConceptFilterConnectionField(AristotleFilterConnectionField):
    def __init__(self, type, *args, **kwargs):

        extrameta = {
            'filterset_base_class': ConceptFilterSet,
        }

        kwargs.update({'extra_filter_meta': extrameta})
        if "description" not in kwargs.keys():
            kwargs['description'] = "Look up a collection of " + str(type._meta.model.get_verbose_name_plural())

        super(AristotleFilterConnectionField, self).__init__(type, *args, **kwargs)
