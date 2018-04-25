from graphene import relay
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from comet import models as comet_models

class IndicatorTypeNode(AristotleObjectType):

    class Meta:
        model=comet_models.IndicatorType
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'

class IndicatorNode(AristotleObjectType):

    class Meta:
        model=comet_models.Indicator
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'

class IndicatorSetTypeNode(AristotleObjectType):

    class Meta:
        model=comet_models.IndicatorSetType
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'

class IndicatorSetNode(AristotleObjectType):

    class Meta:
        model=comet_models.IndicatorSet
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'

class OutcomeAreaNode(AristotleObjectType):

    class Meta:
        model=comet_models.OutcomeArea
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'

class QualityStatementNode(AristotleObjectType):

    class Meta:
        model=comet_models.QualityStatement
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'

class FrameworkNode(AristotleObjectType):

    class Meta:
        model=comet_models.Framework
        interfaces=interfaces = (relay.Node, )
        filter_fields = '__all__'


class Query(object):

    indicator_types = AristotleFilterConnectionField(IndicatorTypeNode)
    indicators = AristotleFilterConnectionField(IndicatorNode)
    indicator_sets = AristotleFilterConnectionField(IndicatorSetNode)
    indicator_set_types = AristotleFilterConnectionField(IndicatorSetTypeNode)
    outcome_areas = AristotleFilterConnectionField(OutcomeAreaNode)
    quality_statements = AristotleFilterConnectionField(QualityStatementNode)
    frameworks = AristotleFilterConnectionField(FrameworkNode)
