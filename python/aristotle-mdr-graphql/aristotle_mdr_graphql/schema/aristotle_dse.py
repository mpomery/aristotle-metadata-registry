from graphene import relay
from graphene_django.types import DjangoObjectType
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField, AristotleConceptFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from aristotle_dse import models as dse_models
from aristotle_mdr_graphql.utils import type_from_model, type_from_concept_model
from aristotle_mdr_graphql import resolvers

# DataCatalogNode = type_from_concept_model(dse_models.DataCatalog)
# DatasetNode = type_from_concept_model(dse_models.Dataset)
# DistributionNode = type_from_concept_model(dse_models.Distribution)
# DistributionDataElementPathNode = type_from_model(dse_models.DistributionDataElementPath)
DataSetSpecificationNode = type_from_concept_model(
    dse_models.DataSetSpecification,
    resolver=resolvers.DataSetSpecificationResolver(),
    meta_kwargs={"exclude_fields": ['data_elements']}
)
# DSSDEInclusionNode = type_from_model(dse_models.DSSDEInclusion)
# DSSClusterInclusionNode = type_from_model(dse_models.DSSClusterInclusion)

class DSSDEInclusionNode(DjangoObjectType):
    class Meta:
        model = dse_models.DSSDEInclusion
        default_resolver = resolvers.DSSInclusionResolver()

class DSSClusterInclusionNode(DjangoObjectType):
    class Meta:
        model = dse_models.DSSClusterInclusion
        default_resolver = resolvers.DSSInclusionResolver()


class Query(object):

    # data_catalogs = AristotleConceptFilterConnectionField(DataCatalogNode)
    # datasets = AristotleConceptFilterConnectionField(DatasetNode)
    # distributions = AristotleConceptFilterConnectionField(DistributionNode)
    dataset_specifications = AristotleConceptFilterConnectionField(DataSetSpecificationNode)
