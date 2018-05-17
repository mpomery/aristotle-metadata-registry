from braces.views import LoginRequiredMixin, PermissionRequiredMixin


from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView
from django.db.models import Q


class RegistryOwnerUserList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name='aristotle_mdr/users_management/users/list.html'

    permission_required = "aristotle_mdr.list_registry_users"
    raise_exception = True
    redirect_unauthenticated_users = True

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        queryset = get_user_model().objects.all().order_by(
            '-is_active', 'full_name', 'short_name', 'email'
        )
        if q:
            queryset = queryset.filter(
                Q(short_name__icontains=q) |
                Q(full_name__icontains=q) |
                Q(email__icontains=q)
            )
        return queryset


class DeactivateRegistryUser(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name='aristotle_mdr/users_management/users/deactivate.html'

    permission_required = "aristotle_mdr.deactivate_registry_users"
    raise_exception = True
    redirect_unauthenticated_users = True

    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        deactivated_user = self.kwargs.get('user_pk')
        deactivated_user = get_object_or_404(get_user_model(), pk=deactivated_user)
        deactivated_user.is_active = False
        deactivated_user.save()
        return redirect(reverse("aristotle-user:registry_user_list"))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        deactivate_user = self.kwargs.get('user_pk')
        if not deactivate_user:
            raise Http404

        deactivate_user = get_object_or_404(get_user_model(), pk=deactivate_user)

        data['deactivate_user'] = deactivate_user
        return data


class ReactivateRegistryUser(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name='aristotle_mdr/users_management/users/reactivate.html'

    permission_required = "aristotle_mdr.reactivate_registry_users"
    raise_exception = True
    redirect_unauthenticated_users = True

    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        reactivated_user = self.kwargs.get('user_pk')
        reactivated_user = get_object_or_404(get_user_model(), pk=reactivated_user)
        reactivated_user.is_active = True
        reactivated_user.save()
        return redirect(reverse("aristotle-user:registry_user_list"))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        reactivate_user = self.kwargs.get('user_pk')
        if not reactivate_user:
            raise Http404

        reactivate_user = get_object_or_404(get_user_model(), pk=reactivate_user)

        data['reactivate_user'] = reactivate_user
        return data
