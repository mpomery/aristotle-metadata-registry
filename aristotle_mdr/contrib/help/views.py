from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from aristotle_mdr.contrib.help.models import ConceptHelp, HelpPage
from aristotle_mdr.utils import fetch_metadata_apps
from django.db.models import Q


class AppHelpViewer(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.app_label:
            self.app = self.object.app_label
            context['app'] = apps.get_app_config(self.app)
        return context


class AllHelpView(ListView):
    template_name = "aristotle_mdr_help/all_help.html"

    def get_queryset(self):
        return HelpPage.objects.filter(
            Q(app_label__in=fetch_metadata_apps()) |
            Q(app_label__isnull=True)
        )


class AllConceptHelpView(ListView):
    template_name = "aristotle_mdr_help/all_concept_help.html"

    def get_queryset(self):
        return ConceptHelp.objects.filter(
            Q(app_label__in=fetch_metadata_apps()) |
            Q(app_label__isnull=True)
        )


class ConceptAppHelpView(ListView):
    template_name = "aristotle_mdr_help/app_concept_help.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = apps.get_app_config(self.kwargs['app'])
        if self.kwargs['app'] not in fetch_metadata_apps():
            raise Http404
        return context

    def get_queryset(self, *args, **kwargs):
        return ConceptHelp.objects.filter(
            app_label__in=fetch_metadata_apps()
        ).filter(app_label=self.kwargs['app'])


class HelpView(AppHelpViewer):
    template_name = "aristotle_mdr_help/regular_help.html"
    model = HelpPage


class ConceptHelpView(AppHelpViewer):
    template_name = "aristotle_mdr_help/concept_help.html"

    def get_object(self, queryset=None):
        if self.kwargs['app'] not in fetch_metadata_apps():
            raise Http404
        app = self.kwargs['app']
        model = self.kwargs['model']
        return get_object_or_404(ConceptHelp, app_label=app, concept_type=model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        model = self.kwargs['model']

        ct = ContentType.objects.get(app_label=self.app, model=model)
        context['model'] = ct.model_class()
        return context
