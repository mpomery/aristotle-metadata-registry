from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.fields import DjangoConnectionField, DjangoListField
from graphene import Field
from aristotle_mdr import models as mdr_models
from django.db import models
import django_filters
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_mdr_graphql.types import AristotleObjectType
from aristotle_mdr_graphql.utils import type_from_model


ConceptNode = type_from_model(mdr_models._concept)
WorkgroupNode = type_from_model(mdr_models.Workgroup)
OrganizationNode = type_from_model(mdr_models.Organization)
RegistrationAuthorityNode = type_from_model(mdr_models.RegistrationAuthority)
ReviewRequestNode = type_from_model(mdr_models.ReviewRequest)
StatusNode = type_from_model(mdr_models.Status)
ObjectClassNode = type_from_model(mdr_models.ObjectClass)
PropertyNode = type_from_model(mdr_models.Property)
MeasureNode = type_from_model(mdr_models.Measure)
UnitOfMeasureNode = type_from_model(mdr_models.UnitOfMeasure)
DataTypeNode = type_from_model(mdr_models.DataType)
ConceptualDomainNode = type_from_model(mdr_models.ConceptualDomain)
ValueMeaningNode = type_from_model(mdr_models.ValueMeaning)
ValueDomainNode = type_from_model(mdr_models.ValueDomain)
PermissibleValueNode = type_from_model(mdr_models.PermissibleValue)
SupplementaryValueNode = type_from_model(mdr_models.SupplementaryValue)
DataElementConceptNode = type_from_model(mdr_models.DataElementConcept)
DataElementNode = type_from_model(mdr_models.DataElement)
DataElementDerivationNode = type_from_model(mdr_models.DataElementDerivation)


class Query(object):

    metadata = AristotleFilterConnectionField(ConceptNode)
    workgroups = AristotleFilterConnectionField(WorkgroupNode)
    organizations = AristotleFilterConnectionField(OrganizationNode)
    registration_authorities = AristotleFilterConnectionField(RegistrationAuthorityNode)
    #discussion_posts = AristotleFilterConnectionField(DiscussionPostNode)
    #discussion_comments = AristotleFilterConnectionField(DiscussionCommentNode)
    review_requests = AristotleFilterConnectionField(ReviewRequestNode)
    object_classes = AristotleFilterConnectionField(ObjectClassNode)
    properties = AristotleFilterConnectionField(PropertyNode)
    measures = AristotleFilterConnectionField(MeasureNode)
    unit_of_measures = AristotleFilterConnectionField(UnitOfMeasureNode)
    data_types = AristotleFilterConnectionField(DataTypeNode)
    conceptual_domains = AristotleFilterConnectionField(ConceptualDomainNode)
    value_domains = AristotleFilterConnectionField(ValueDomainNode)
    data_element_concepts = AristotleFilterConnectionField(DataElementConceptNode)
    data_elements = AristotleFilterConnectionField(DataElementNode)
    data_element_derivations = AristotleFilterConnectionField(DataElementDerivationNode)
