from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.fields import DjangoConnectionField
from graphene_django.utils import maybe_queryset
from django.db import models
import django_filters

import logging
logger = logging.getLogger(__name__)

class AristotleFilterConnectionField(DjangoFilterConnectionField):

    def __init__(self, *args, **kwargs):

        extrameta = {
            'filter_overrides': {
                models.CharField: {
                     'filter_class': django_filters.CharFilter,
                     'extra': lambda f: {
                         'lookup_expr': 'iexact'
                     }
                 },
                 models.TextField: {
                    'filter_class': django_filters.CharFilter,
                    'extra': lambda f: {
                        'lookup_expr': 'iexact'
                    }
                 }
            }
        }
        
        kwargs.update({'extra_filter_meta': extrameta})
        super().__init__(*args, **kwargs)

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
