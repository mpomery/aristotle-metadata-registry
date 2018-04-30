from graphene import relay
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from aristotle_dse import models as dse_models
from aristotle_mdr_graphql.utils import type_from_model

DataCatalogNode = type_from_model(dse_models.DataCatalog)
DatasetNode = type_from_model(dse_models.Dataset)
DistributionNode = type_from_model(dse_models.Distribution)
DistributionDataElementPathNode = type_from_model(dse_models.DistributionDataElementPath)
DataSetSpecificationNode = type_from_model(dse_models.DataSetSpecification)
DSSDEInclusionNode = type_from_model(dse_models.DSSDEInclusion)
DSSClusterInclusionNode = type_from_model(dse_models.DSSClusterInclusion)


class Query(object):

    data_catalogs = AristotleFilterConnectionField(DataCatalogNode)
    datasets = AristotleFilterConnectionField(DatasetNode)
    distributions = AristotleFilterConnectionField(DistributionNode)
    distribution_data_element_paths = AristotleFilterConnectionField(DistributionDataElementPathNode)
    dataset_specifications = AristotleFilterConnectionField(DataSetSpecificationNode)
    dssde_inclusions = AristotleFilterConnectionField(DSSDEInclusionNode)
    dss_cluster_inclusions = AristotleFilterConnectionField(DSSClusterInclusionNode)
