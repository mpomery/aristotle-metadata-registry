from graphene_django.types import DjangoObjectType
from aristotle_mdr import models as mdr_models
from graphene import relay
from django.db.models import Model
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

import logging
logger = logging.getLogger(__name__)

def aristotle_resolver(attname, default_value, root, info, **args):
    retval = getattr(root, attname, default_value)

    #logger.debug('retval type is {}'.format(type(retval)))

    # If object is a django model
    if isinstance(retval, Model):

        # If model has can_view method
        if hasattr(retval, 'can_view'):

            # Use can_view to determine if we display
            if retval.can_view(info.context.user):
                return retval
            else:
                return None
        else:

            # If no can_view method return value
            return retval

    elif isinstance(retval, Manager):

        # Need this for when related manager is returned when querying object.related_set
        # Can safely return restricted queryset
        return retval.get_queryset().visible(info.context.user)

    elif isinstance(retval, QuerySet):

        # In case a queryset is returned
        return retval.visible(info.context.user)

    return retval


class AristotleObjectType(DjangoObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = '__all__'

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):
        kwargs.update({'default_resolver': aristotle_resolver})
        super().__init_subclass_with_meta__(*args, **kwargs)
