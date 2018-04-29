from graphene import relay
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from comet import models as comet_models

class IndicatorTypeNode(AristotleObjectType):

    class Meta:
        model=comet_models.IndicatorType

class IndicatorNode(AristotleObjectType):

    class Meta:
        model=comet_models.Indicator

class IndicatorSetTypeNode(AristotleObjectType):

    class Meta:
        model=comet_models.IndicatorSetType

class IndicatorSetNode(AristotleObjectType):

    class Meta:
        model=comet_models.IndicatorSet

class OutcomeAreaNode(AristotleObjectType):

    class Meta:
        model=comet_models.OutcomeArea

class QualityStatementNode(AristotleObjectType):

    class Meta:
        model=comet_models.QualityStatement

class FrameworkNode(AristotleObjectType):

    class Meta:
        model=comet_models.Framework


class Query(object):

    indicator_types = AristotleFilterConnectionField(IndicatorTypeNode)
    indicators = AristotleFilterConnectionField(IndicatorNode)
    indicator_sets = AristotleFilterConnectionField(IndicatorSetNode)
    indicator_set_types = AristotleFilterConnectionField(IndicatorSetTypeNode)
    outcome_areas = AristotleFilterConnectionField(OutcomeAreaNode)
    quality_statements = AristotleFilterConnectionField(QualityStatementNode)
    frameworks = AristotleFilterConnectionField(FrameworkNode)
