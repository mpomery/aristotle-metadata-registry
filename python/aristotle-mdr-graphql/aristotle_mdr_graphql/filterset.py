from django_filters.filterset import FilterSet
from django_filters.constants import ALL_FIELDS
from django_filters.utils import get_all_model_fields
import django_filters
from django.db import models
from aristotle_mdr.models import _concept


class AristotleFilterSet(FilterSet):
    pass

    # @classmethod
    # def get_fields(cls):

    #     model = cls._meta.model
    #     fields = cls._meta.fields
    #     exclude = cls._meta.exclude
    #     logger.warning([model,fields,exclude])

    #     # Setting exclude with no fields implies all other fields.
    #     if exclude is not None and fields is None:
    #         fields = ALL_FIELDS

    #     # Resolve ALL_FIELDS into all fields for the filterset's model.
    #     if fields == ALL_FIELDS:
    #         fields = get_all_model_fields(model)

    #     if not isinstance(fields, dict):

    #         field_dict = {}

    #         for field in fields:
    #             dbfield = model._meta.get_field(field)

    #             if isinstance(dbfield, models.CharField) or isinstance(dbfield, models.TextField):
    #                 field_dict[field] = ['exact', 'icontains', 'iexact']
    #             else:
    #                 field_dict[field] = ['exact']

    #         cls._meta.fields = field_dict

    #     return super().get_fields()


class ConceptFilterSet(FilterSet):

    identifier = django_filters.CharFilter(name='identifiers__identifier', lookup_expr='iexact', distinct=True)
    identifier_namespace = django_filters.CharFilter(name='identifiers__namespace__shorthand_prefix', lookup_expr='iexact', distinct=True)
    identifier_version = django_filters.CharFilter(name='identifiers__version', lookup_expr='iexact', distinct=True)
