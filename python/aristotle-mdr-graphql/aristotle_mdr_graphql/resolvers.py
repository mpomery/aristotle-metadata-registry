import graphene
import logging

from aristotle_mdr import perms
from aristotle_mdr import models as mdr_models
from aristotle_dse import models as dse_models
from django.db.models import Model
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from graphene import relay
from graphene_django.types import DjangoObjectType

logger = logging.getLogger(__name__)


class AristotleResolver(object):
    @classmethod
    def resolver(cls, attname, default_value, root, info, **args):
        retval = getattr(root, attname, default_value)

        # If object is a django model
        if isinstance(retval, Model):
    
            # Use user_can_view to determine if we display
            if perms.user_can_view(info.context.user, retval):
                return retval
            else:
                return None
    
        elif isinstance(retval, Manager):
    
            # Need this for when related manager is returned when querying object.related_set
            # Can safely return restricted queryset
            return retval.get_queryset().visible(info.context.user)
    
        elif isinstance(retval, QuerySet):
    
            # In case a queryset is returned
            return retval.visible(info.context.user)
    
        return retval

    def __call__(self, *args, **kwargs):
        return self.__class__.resolver(*args, **kwargs)


aristotle_resolver = AristotleResolver()


class RegistrationAuthorityResolver(AristotleResolver):
    pass


class ValueDomainResolver(AristotleResolver):
    @classmethod
    def resolver(cls, attname, default_value, root, info, **args):
        retval = getattr(root, attname, default_value)
        logger.debug(str([
            type(retval), isinstance(retval, QuerySet)
            
        ]))
        if root.can_view(info.context.user):
            if isinstance(retval, Manager) and issubclass(retval.model, mdr_models.AbstractValue):
                return retval.get_queryset()
            if isinstance(retval, QuerySet) and issubclass(retval.model, mdr_models.AbstractValue):
                return retval
        return super().resolver(attname, default_value, root, info, **args)


class DataSetSpecificationResolver(AristotleResolver):
    @classmethod
    def resolver(cls, attname, default_value, root, info, **args):
        retval = getattr(root, attname, default_value)
        logger.debug(str([
            retval, type(retval), isinstance(retval, QuerySet)
            
        ]))
        if root.can_view(info.context.user):
            if isinstance(retval, Manager) and issubclass(retval.model, dse_models.DSSInclusion):
                return retval.get_queryset()
            if isinstance(retval, QuerySet) and issubclass(retval.model, dse_models.DSSInclusion):
                return retval
        return super().resolver(attname, default_value, root, info, **args)

class DSSInclusionResolver(AristotleResolver):
    pass
