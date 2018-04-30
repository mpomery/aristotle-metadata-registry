from graphene import relay
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from comet import models as comet_models
from aristotle_mdr_graphql.utils import type_from_model

IndicatorTypeNode = type_from_model(comet_models.IndicatorType)
IndicatorNode = type_from_model(comet_models.Indicator)
IndicatorSetTypeNode = type_from_model(comet_models.IndicatorSetType)
IndicatorSetNode = type_from_model(comet_models.IndicatorSet)
OutcomeAreaNode = type_from_model(comet_models.OutcomeArea)
QualityStatementNode = type_from_model(comet_models.QualityStatement)
FrameworkNode = type_from_model(comet_models.Framework)


class Query(object):

    indicator_types = AristotleFilterConnectionField(IndicatorTypeNode)
    indicators = AristotleFilterConnectionField(IndicatorNode)
    indicator_sets = AristotleFilterConnectionField(IndicatorSetNode)
    indicator_set_types = AristotleFilterConnectionField(IndicatorSetTypeNode)
    outcome_areas = AristotleFilterConnectionField(OutcomeAreaNode)
    quality_statements = AristotleFilterConnectionField(QualityStatementNode)
    frameworks = AristotleFilterConnectionField(FrameworkNode)
