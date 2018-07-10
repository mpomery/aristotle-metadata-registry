from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.fields import DjangoConnectionField, DjangoListField
from graphene import Field
from django.db import models

from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.identifiers import models as ident_models
from aristotle_mdr.contrib.slots import models as slot_models
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField, AristotleConceptFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from aristotle_mdr_graphql.utils import type_from_model, type_from_concept_model

from aristotle_mdr_graphql import resolvers
from aristotle_mdr_graphql.filterset import ConceptFilterSet


class StatusNode(DjangoObjectType):
    class Meta:
        model = mdr_models.Status
        default_resolver = resolvers.aristotle_resolver


WorkgroupNode = type_from_model(mdr_models.Workgroup)
# OrganizationNode = type_from_model(mdr_models.Organization)

class RegistrationAuthorityNode(DjangoObjectType):
    # At the moment, querying backward for a status from a registration authority has
    # permissions issues, and querying problems.
    # Lets come back to this one
    class Meta:
        model = mdr_models.RegistrationAuthority
        interfaces = (relay.Node, )
        filter_fields = ['name']
        default_resolver = resolvers.RegistrationAuthorityResolver()
        exclude_fields = ['status_set']


# ReviewRequestNode = type_from_model(mdr_models.ReviewRequest)

ConceptNode = type_from_concept_model(mdr_models._concept)
ObjectClassNode = type_from_concept_model(mdr_models.ObjectClass)
PropertyNode = type_from_concept_model(mdr_models.Property)
# MeasureNode = type_from_concept_model(mdr_models.Measure)
UnitOfMeasureNode = type_from_concept_model(mdr_models.UnitOfMeasure)
DataTypeNode = type_from_concept_model(mdr_models.DataType)
ConceptualDomainNode = type_from_concept_model(mdr_models.ConceptualDomain)
ValueMeaningNode = type_from_model(mdr_models.ValueMeaning)

# Slots and Identifiers

class ScopedIdentifierNode(DjangoObjectType):
    class Meta:
        model = ident_models.ScopedIdentifier

SlotNode = type_from_model(slot_models.Slot)

class ValueMeaningNode(DjangoObjectType):
    class Meta:
        model = mdr_models.ValueMeaning

ValueDomainNode = type_from_concept_model(
    mdr_models.ValueDomain,
    resolver = resolvers.ValueDomainResolver()
)

DataElementNode = type_from_concept_model(
    mdr_models.DataElement,
    extra_filter_fields=['dataElementConcept','valueDomain','dataElementConcept__objectClass'],
)

DataElementConceptNode = type_from_model(mdr_models.DataElementConcept)
DataElementDerivationNode = type_from_concept_model(mdr_models.DataElementDerivation)


class PermissibleValueNode(DjangoObjectType):
    class Meta:
        model = mdr_models.PermissibleValue
        exclude_fields = ['value_meaning']

class SupplementaryValueNode(DjangoObjectType):
    class Meta:
        model = mdr_models.SupplementaryValue
        exclude_fields = ['value_meaning']


class Query(object):

    metadata = AristotleConceptFilterConnectionField(
        ConceptNode,
        description="Retrieve a collection of untyped metadata",
    )
    workgroups = AristotleFilterConnectionField(WorkgroupNode)
    # organizations = AristotleFilterConnectionField(OrganizationNode)
    registration_authorities = DjangoFilterConnectionField(RegistrationAuthorityNode)
    #discussion_posts = AristotleFilterConnectionField(DiscussionPostNode)
    #discussion_comments = AristotleFilterConnectionField(DiscussionCommentNode)
    # review_requests = AristotleFilterConnectionField(ReviewRequestNode)

    object_classes = AristotleConceptFilterConnectionField(ObjectClassNode)
    properties = AristotleConceptFilterConnectionField(PropertyNode)
    # measures = AristotleConceptFilterConnectionField(MeasureNode)
    unit_of_measures = AristotleConceptFilterConnectionField(UnitOfMeasureNode)
    data_types = AristotleConceptFilterConnectionField(DataTypeNode)
    conceptual_domains = AristotleConceptFilterConnectionField(ConceptualDomainNode)
    value_domains = AristotleConceptFilterConnectionField(ValueDomainNode)
    data_element_concepts = AristotleConceptFilterConnectionField(DataElementConceptNode)
    data_elements = AristotleConceptFilterConnectionField(DataElementNode)
    data_element_derivations = AristotleConceptFilterConnectionField(DataElementDerivationNode)
