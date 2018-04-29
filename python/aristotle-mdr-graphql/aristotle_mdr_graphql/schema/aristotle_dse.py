from graphene import relay
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from aristotle_dse import models as dse_models

class DataCatalogNode(AristotleObjectType):

    class Meta:
        model=dse_models.DataCatalog

class DatasetNode(AristotleObjectType):

    class Meta:
        model=dse_models.Dataset

class DistributionNode(AristotleObjectType):

    class Meta:
        model=dse_models.Distribution

class DistributionDataElementPathNode(AristotleObjectType):

    class Meta:
        model=dse_models.DistributionDataElementPath

class DataSetSpecificationNode(AristotleObjectType):

    class Meta:
        model=dse_models.DataSetSpecification

class DSSDEInclusionNode(AristotleObjectType):

    class Meta:
        model=dse_models.DSSDEInclusion

class DSSClusterInclusionNode(AristotleObjectType):

    class Meta:
        model=dse_models.DSSClusterInclusion


class Query(object):

    data_catalogs = AristotleFilterConnectionField(DataCatalogNode)
    datasets = AristotleFilterConnectionField(DatasetNode)
    distributions = AristotleFilterConnectionField(DistributionNode)
    distribution_data_element_paths = AristotleFilterConnectionField(DistributionDataElementPathNode)
    dataset_specifications = AristotleFilterConnectionField(DataSetSpecificationNode)
    dssde_inclusions = AristotleFilterConnectionField(DSSDEInclusionNode)
    dss_cluster_inclusions = AristotleFilterConnectionField(DSSClusterInclusionNode)
