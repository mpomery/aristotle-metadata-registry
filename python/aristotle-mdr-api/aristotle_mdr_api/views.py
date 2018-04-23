from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class APIRootView(TemplateView):
    template_name = "aristotle_mdr_api/base.html"
