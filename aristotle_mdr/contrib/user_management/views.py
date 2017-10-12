from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView, DetailView, FormView


from organizations.backends import registration_backend

from .org_backends import NewuserOnlyRegistrationBackend

from . import forms

class NewUserSignupView(FormView):
    """
    View that allows unregistered users to create an organization account.
    It simply processes the form and then calls the specified registration
    backend.
    """
    form_class = forms.RegistrySignUpForm
    template_name='aristotle_mdr/users_management/newuser/signup.html'
    # TODO get success from backend, because some backends may do something
    # else, like require verification
    backend = NewuserOnlyRegistrationBackend

