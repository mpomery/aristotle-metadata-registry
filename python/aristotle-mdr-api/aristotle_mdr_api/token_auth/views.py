from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from aristotle_mdr_api.token_auth.models import AristotleToken
from aristotle_mdr_api.token_auth.forms import TokenCreateForm

import json

class TokenListView(LoginRequiredMixin, ListView):
    template_name = "aristotle_mdr_api/token.html"

    def get_queryset(self):
        return AristotleToken.objects.filter(user=self.request.user).order_by('created')


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

    def get_context_data(self):
        context = super().get_context_data()
        context['submit_text'] = 'Create Token'
        return context

class TokenUpdateView(LoginRequiredMixin, FormView):
    form_class = TokenCreateForm
    template_name = "aristotle_mdr_api/token_create.html"

    def get_token(self):
        token_id = self.kwargs['token_id']

        try:
            token = AristotleToken.objects.get(pk=token_id, user=self.request.user)
        except AristotleToken.DoesNotExist:
            return None

        return token

    def form_valid(self, form):
        token = self.get_token()

        if token is None:
            return self.render_to_response({'error': 'Token could not be updated'})

        token.name = form.cleaned_data['name']
        token.permissions = form.cleaned_data['perm_json']
        token.save()

        return self.render_to_response({'message': 'Your token has been updated'})

    def get_initial(self):

        token = self.get_token()

        if token is None:
            return {}

        initial = {
            'name': token.name,
            'perm_json': json.dumps(token.permissions)
        }

        return initial

    def get_context_data(self):

        context = super().get_context_data()

        context['token_id'] = self.kwargs['token_id']
        context['submit_text'] = 'Update Token'

        if not context['form'].initial:
            context['error'] = 'Token could not be found'
            context.pop('form')

        if 'error' not in context:
            context['display_regenerate'] = True

        return context


class TokenRegenerateView(LoginRequiredMixin, TemplateView):
    template_name = "aristotle_mdr_api/token_create.html"

    def get(self, request, *args, **kwargs):
        token_id = self.kwargs['token_id']

        try:
            token = AristotleToken.objects.get(id=token_id, user=self.request.user)
        except AristotleToken.DoesNotExist:
            return self.render_to_response({'error': 'Could not regenerate token'})

        token.key = token.generate_key()
        token.save()

        return self.render_to_response({'key': token.key})


class TokenDeleteView(LoginRequiredMixin, DeleteView):
    model = AristotleToken
    pk_url_kwarg = 'token_id'
    template_name = 'aristotle_mdr_api/token_delete.html'

    def get_queryset(self):
        return AristotleToken.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('token_auth:token_list')
