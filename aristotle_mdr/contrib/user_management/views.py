from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView, DetailView, FormView


from organizations.backends import registration_backend

# from .org_backends import NewuserOnlyRegistrationBackend

from . import forms

class RegistryOwnerUserList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name='aristotle_mdr/users_management/users/list.html'

    permission_required = "aristotle_mdr.list_registry_users"
    raise_exception = True
    redirect_unauthenticated_users = True

    def get_queryset(self):
        return get_user_model().objects.all()


class DeactivateRegistryUser(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name='aristotle_mdr/users_management/users/deactivate.html'

    permission_required = "aristotle_mdr.deactivate_registry_users"
    raise_exception = True
    redirect_unauthenticated_users = True

    http_method_names = ['get','post']

    def post(self, request, *args, **kwargs):
        deactivated_user = self.request.POST.get('deactivate_user')
        deactivated_user = get_object_or_404(get_user_model(), pk=deactivated_user)
        deactivated_user.is_active = False
        deactivated_user.save()
        return redirect(reverse("aristotle-user:registry_user_list"))

    def get_context_data(self, **kwargs):
        data = super(DeactivateRegistryUser, self).get_context_data(**kwargs)
        deactivate_user = self.request.GET.get('deactivate_user')
        if not deactivate_user:
            raise Http404

        deactivate_user = get_object_or_404(get_user_model(), pk=deactivate_user)

        data['deactivate_user'] = deactivate_user
        return data
