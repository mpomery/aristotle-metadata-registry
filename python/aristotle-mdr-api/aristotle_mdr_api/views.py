from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from aristotle_mdr_api.models import AristotleToken
from aristotle_mdr_api.forms import TokenCreateForm


class APIRootView(TemplateView):
    template_name = "aristotle_mdr_api/base.html"


class TokenListView(LoginRequiredMixin, ListView):
    template_name = "aristotle_mdr_api/token.html"

    def get_queryset(self):
        return AristotleToken.objects.filter(user=self.request.user)


class TokenCreateView(LoginRequiredMixin, FormView):
    form_class = TokenCreateForm
    template_name = "aristotle_mdr_api/token_create.html"

    def form_valid(self, form):
        token = AristotleToken.objects.create(
            name=form.cleaned_data['name'],
            permissions=form.cleaned_data['perm_json'],
            user=self.request.user
        )
        return self.render_to_response({'key': token.key})
