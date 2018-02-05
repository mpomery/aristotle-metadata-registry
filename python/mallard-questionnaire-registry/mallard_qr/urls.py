from django.conf.urls import include, url

#from mallard_qr import views#,forms
from django.views.generic import TemplateView
from aristotle_mdr.contrib.generic.views import GenericAlterOneToManyView

from aristotle_mdr.models import ValueDomain

from . import models
urlpatterns = [
    url(r'^question/(?P<iid>\d+)/responses/?$',
        GenericAlterOneToManyView.as_view(
            model_base = models.Question,
            model_to_add = models.ResponseDomain,
            model_base_field = 'response_domains',
            model_to_add_field = 'question',
            ordering_field = 'order',
        ), name='question_alter_responses'),

#These are required for about pages to work. Include them, or custom items will die!
#    url(r'^about/(?P<template>.+)/?$', views.DynamicTemplateView.as_view(), name="about"),
#    url(r'^about/?$', TemplateView.as_view(template_name='comet/static/about_comet_mdr.html'), name="about"),
]
