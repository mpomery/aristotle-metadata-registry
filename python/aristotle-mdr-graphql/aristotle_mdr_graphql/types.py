from graphene_django.types import DjangoObjectType
from aristotle_mdr import models as mdr_models
from graphene import relay
from django.db.models import Model

def aristotle_resolver(attname, default_value, root, info, **args):
    retval = getattr(root, attname, default_value)

    if isinstance(retval, Model):

        if hasattr(retval, 'can_view'):
            if retval.can_view(info.context.user):
                return retval
            else:
                return None
        else:
            return retval

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
