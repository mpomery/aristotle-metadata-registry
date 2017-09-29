from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify

from django.views.generic import CreateView, ListView, DetailView, UpdateView

from aristotle_mdr import models as MDR
from aristotle_mdr import forms as MDRForms
from aristotle_mdr.views.utils import (
    workgroup_item_statuses,
    paginated_list,
    paginated_workgroup_list,
    paginated_registration_authority_list,
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


class CreateRegistrationAuthority(CreateView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/add.html"
    fields = ['name', 'definition']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                reverse('friendly_login') + '?next=%s' % request.path
            )
        if not request.user.has_perm("aristotle_mdr.add_registration_authority"):
            raise PermissionDenied
        return super(CreateRegistrationAuthority, self).dispatch(request, *args, **kwargs)


class ListRegistrationAuthority(ListView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/list_all.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                reverse('friendly_login') + '?next=%s' % request.path
            )
        if not request.user.has_perm("aristotle_mdr.is_registry_administrator"):
            raise PermissionDenied
        ras = MDR.RegistrationAuthority.objects.all()

        text_filter = request.GET.get('filter', "")
        if text_filter:
            ras = ras.filter(Q(name__icontains=text_filter) | Q(definition__icontains=text_filter))
        context = {'filter': text_filter}
        return paginated_registration_authority_list(request, ras, self.template_name, context)
        # return super(ListRegistrationAuthority, self).dispatch(request, *args, **kwargs)


class ManageRegistrationAuthority(DetailView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/manage.html"

    pk_url_kwarg = 'iid'
    context_object_name = "item"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                reverse('friendly_login') + '?next=%s' % request.path
            )
        if not request.user.has_perm("aristotle_mdr.change_registration_authority"):
            raise PermissionDenied
        return super(ManageRegistrationAuthority, self).dispatch(request, *args, **kwargs)


class EditRegistrationAuthority(UpdateView):
    model = MDR.RegistrationAuthority
    template_name = "aristotle_mdr/user/registration_authority/edit.html"

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

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                reverse('friendly_login') + '?next=%s' % request.path
            )
        if not request.user.has_perm("aristotle_mdr.change_registration_authority"):
            raise PermissionDenied
        return super(EditRegistrationAuthority, self).dispatch(request, *args, **kwargs)
