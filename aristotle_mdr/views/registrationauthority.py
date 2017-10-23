from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify

from django.views.generic import CreateView, ListView, DetailView, UpdateView, FormView

from aristotle_mdr import models as MDR
from aristotle_mdr import forms as MDRForms
from aristotle_mdr.views.utils import (
    workgroup_item_statuses,
    paginated_list,
    paginated_workgroup_list,
    paginated_registration_authority_list,
    ObjectLevelPermissionRequiredMixin
)

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


def registrationauthority(request, iid, *args, **kwargs):
    if iid is None:
        return redirect(reverse("aristotle_mdr:all_registration_authorities"))
    item = get_object_or_404(MDR.RegistrationAuthority, pk=iid).item

    return render(request, item.template, {'item': item.item})


def organization(request, iid, *args, **kwargs):
    if iid is None:
        return redirect(reverse("aristotle_mdr:all_organizations"))
    item = get_object_or_404(MDR.Organization, pk=iid).item

    return render(request, item.template, {'item': item.item})


def all_registration_authorities(request):
    ras = MDR.RegistrationAuthority.objects.order_by('name')
    return render(request, "aristotle_mdr/organization/all_registration_authorities.html", {'registrationAuthorities': ras})


def all_organizations(request):
    orgs = MDR.Organization.objects.order_by('name')
    return render(request, "aristotle_mdr/organization/all_organizations.html", {'organization': orgs})


class CreateRegistrationAuthority(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = "aristotle_mdr/user/registration_authority/add.html"
    fields = ['name', 'definition']
    permission_required = "aristotle_mdr.add_registration_authority"
    raise_exception = True
    redirect_unauthenticated_users = True


class AddUser(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/add_user.html"
    permission_required = "aristotle_mdr.change_registrationauthority_memberships"
    raise_exception = True
    redirect_unauthenticated_users = True
    form_class = MDRForms.actions.AddRegistrationUserForm

    def get_form_kwargs(self):
        kwargs = super(AddUser, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(MDR.RegistrationAuthority, pk=self.kwargs.get('iid'))
        return super(AddUser, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        kwargs = super(AddUser, self).get_context_data(**kwargs)
        kwargs.update({'item': self.item})
        return kwargs

    def form_valid(self, form):
        user = form.cleaned_data['user']
        for role in form.cleaned_data['roles']:
            self.item.giveRoleToUser(role, user)

        return redirect(reverse('aristotle:registrationauthority_manage', args=[self.item.id]))


class ListRegistrationAuthority(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/list_all.html"
    permission_required = "aristotle_mdr.is_registry_administrator"
    raise_exception = True
    redirect_unauthenticated_users = True

    def dispatch(self, request, *args, **kwargs):
        super(ListRegistrationAuthority, self).dispatch(request, *args, **kwargs)
        ras = MDR.RegistrationAuthority.objects.all()

        text_filter = request.GET.get('filter', "")
        if text_filter:
            ras = ras.filter(Q(name__icontains=text_filter) | Q(definition__icontains=text_filter))
        context = {'filter': text_filter}
        return paginated_registration_authority_list(request, ras, self.template_name, context)


class ManageRegistrationAuthority(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/manage.html"
    permission_required = "aristotle_mdr.change_registrationauthority"
    raise_exception = True
    redirect_unauthenticated_users = True

    pk_url_kwarg = 'iid'
    context_object_name = "item"


class EditRegistrationAuthority(LoginRequiredMixin, ObjectLevelPermissionRequiredMixin, UpdateView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/edit.html"
    permission_required = "aristotle_mdr.change_registrationauthority"
    raise_exception = True
    redirect_unauthenticated_users = True
    object_level_permissions = True

    fields = [
        'name',
        'definition',
        'locked_state',
        'public_state',
        'notprogressed',
        'incomplete',
        'candidate',
        'recorded',
        'qualified',
        'standard',
        'preferred',
        'superseded',
        'retired',
    ]

    pk_url_kwarg = 'iid'
    context_object_name = "item"


class ChangeUserRoles(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/change_role.html"
    permission_required = "aristotle_mdr.change_registrationauthority_memberships"
    raise_exception = True
    redirect_unauthenticated_users = True
    form_class = MDRForms.actions.ChangeRegistrationUserRolesForm

    def get_form_kwargs(self):
        kwargs = super(ChangeUserRoles, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        initial = {'roles': []}
        if self.user_to_change in self.item.managers.all():
            initial['roles'].append('manager')
        if self.user_to_change in self.item.registrars.all():
            initial['roles'].append('registrar')
        kwargs.update({'initial': initial})
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(MDR.RegistrationAuthority, pk=self.kwargs.get('iid'))
        self.user_to_change = get_object_or_404(get_user_model(), pk=self.kwargs.get('user_pk'))
        return super(ChangeUserRoles, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        kwargs = super(ChangeUserRoles, self).get_context_data(**kwargs)
        kwargs.update({'item': self.item})
        kwargs.update({'user_to_change': self.user_to_change})

        return kwargs

    def form_valid(self, form):
        for role in MDR.RegistrationAuthority.roles:
            if role in form.cleaned_data['roles']:
                self.item.giveRoleToUser(role, self.user_to_change)
            else:
                self.item.removeRoleFromUser(role, self.user_to_change)

        return redirect(reverse('aristotle:registrationauthority_manage', args=[self.item.id]))
