from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from aristotle_mdr_api.models import AristotleToken
from aristotle_mdr_api.forms import TokenCreateForm


class APIRootView(TemplateView):
    template_name = "aristotle_mdr_api/base.html"


class GetTokenView(LoginRequiredMixin, TemplateView):
    template_name = "aristotle_mdr_api/token.html"

    def get(self, request, *args, **kwargs):

        try:
            token = AristotleToken.objects.get(user=request.user)
        except AristotleToken.DoesNotExist:
            token = AristotleToken.objects.create(user=request.user, permissions={})

        kwargs['token'] = token.key

        return super().get(request, *args, **kwargs)


class TokenCreateView(FormView):
    form_class = TokenCreateForm
    template_name = "aristotle_mdr_api/form.html"
