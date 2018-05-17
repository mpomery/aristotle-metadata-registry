from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.authtoken.models import Token


class APIRootView(TemplateView):
    template_name = "aristotle_mdr_api/base.html"


class GetTokenView(LoginRequiredMixin, TemplateView):
    template_name = "aristotle_mdr_api/token.html"

    def get(self, request, *args, **kwargs):

        token, created = Token.objects.get_or_create(user=request.user)
        kwargs['token'] = token.key

        return super().get(request, *args, **kwargs)
