from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.fields import DjangoConnectionField
from graphene_django.utils import maybe_queryset

import logging
logger = logging.getLogger(__name__)

class AristotleFilterConnectionField(DjangoFilterConnectionField):

    def __init__(self, type, *args, **kwargs):

        super().__init__(type, *args, **kwargs)
        logger.debug('Initing afcf with type {0}'.format(type))
        logger.debug('Fields are {0}'.format(self._fields))

    @classmethod
    def connection_resolver(cls, resolver, connection, default_manager, max_limit,
                            enforce_first_or_last, filterset_class, filtering_args,
                            root, info, **args):

        logger.debug(info.context.user)

        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        qs = filterset_class(
            data=filter_kwargs,
            queryset=default_manager.get_queryset(),
            request=info.context
        ).qs

        qs = qs.visible(info.context.user)
        logger.debug('getting connection resolver with args {0}'.format(filtering_args))

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

    @classmethod
    def resolve_connection(self, connection, default_manager, args, iterable):
        logger.debug('resolving connection {}'.format(iterable))
        logger.debug('args are {}'.format(args))
        return super().resolve_connection(connection, default_manager, args, iterable)

    @classmethod
    def merge_querysets(cls, default_queryset, queryset):
        logger.debug('we merging')
        return super().merge_querysets(default_queryset, queryset)
