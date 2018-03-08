from django.conf.urls import include, url

from comet import views
from django.views.generic import TemplateView
from aristotle_mdr.contrib.generic.views import GenericAlterManyToManyView
from comet import models


urlpatterns = [
    url(r'^/?$', TemplateView.as_view(template_name='comet/static/about_comet_mdr.html')),
    url(
        r'^outcome_area/(?P<iid>\d+)/add_indicators/?$',
        views.OutcomeAlterIndicators.as_view(),
        name='outcomearea_alter_indicators'
    ),
    url(r'^outcome_area/(?P<iid>\d+)/add_indicators/?$',
        GenericAlterManyToManyView.as_view(
            model_base = models.OutcomeArea,
            model_to_add = models.Indicator,
            model_base_field = 'indicators',
        ),
        name='outcomearea_alter_indicators'
    ),
    url(r'^indicator/(?P<iid>\d+)/add_outcome_areas/?$',
        GenericAlterManyToManyView.as_view(
            model_base = models.Indicator,
            model_to_add = models.OutcomeArea,
            model_base_field = 'outcome_areas',
        ),
        name='indicator_alter_outcomeareas'
    ),

#These are required for about pages to work. Include them, or custom items will die!
    url(r'^about/(?P<template>.+)/?$', views.DynamicTemplateView.as_view(), name="about"),
    url(r'^about/?$', TemplateView.as_view(template_name='comet/static/about_comet_mdr.html'), name="about"),
]
