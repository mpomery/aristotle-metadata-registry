import graphene
import logging

from aristotle_mdr import models as mdr_models
from aristotle_mdr import perms
from graphene import relay
from graphene_django.types import DjangoObjectType

logger = logging.getLogger(__name__)

from aristotle_mdr_graphql import resolvers

class AristotleObjectType(DjangoObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = [] #'__all__'

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):

        kwargs.update({
            'default_resolver': resolvers.aristotle_resolver,
            'interfaces': (relay.Node, ),
        })
        if "filter_fields" not in kwargs.keys():
            kwargs['filter_fields'] = '__all__'
        super().__init_subclass_with_meta__(*args, **kwargs)


class AristotleConceptObjectType(DjangoObjectType):
    metadata_type = graphene.String()

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = '__all__'

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):

        # Default resolver is set in type_from_concept_model instead
        kwargs.update({
            # 'default_resolver': aristotle_resolver,
            'interfaces': (relay.Node, ),
            # 'filter_fields': ['name'],
        })
        super().__init_subclass_with_meta__(*args, **kwargs)

    def resolve_metadata_type(self, info, **kwargs):
        item = self.item
        out = "{}:{}".format(item._meta.app_label,item._meta.model_name)
        return out
