from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, FormView, View
from django.db.models import Q

from organizations.backends.defaults import BaseBackend
from organizations.backends.tokens import RegistrationTokenGenerator

from aristotle_mdr.utils.utils import fetch_aristotle_settings
from . import forms

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


class SignupView(FormView):

    form_class = forms.UserRegistrationForm
    template_name = "aristotle_mdr/users_management/self_invite.html"

    activation_subject = 'aristotle_mdr/users_management/newuser/email/activation_subject.txt'
    activation_body = 'aristotle_mdr/users_management/newuser/email/activation_body.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()
        self.registration_backend = BaseBackend()
        self.if_logged_in_url = reverse('aristotle_mdr:userHome')
        self.users_to_notify = self.user_model.objects.filter(is_superuser=True)

    def dispatch(self, request, *args, **kwargs):
        aristotle_settings = fetch_aristotle_settings()

        if request.user.is_authenticated:
            return HttpResponseRedirect(self.if_logged_in_url)

        try:
            signup_settings = aristotle_settings['registry']['SELF_SIGNUP']
        except KeyError:
            try:
                signup_settings = aristotle_settings['SELF_SIGNUP']
            except KeyError:
                signup_settings = None

        if signup_settings:
            # Check if user self signup is enabled
            self.signup_enabled = signup_settings.get('enabled', False)
            self.allowed_suffixes = signup_settings.get('emails', None)
        else:
            self.signup_enabled = False
            self.allowed_suffixes = None

        if not self.signup_enabled:
            return self.render_to_response({'message': 'Self Signup is not enabled'})

        return super().dispatch(request, *args, **kwargs)

    def validate_email(self, email, suffixes):
        valid = False

        for suffix in suffixes:
            if email.endswith(suffix.strip()):
                valid = True

        return valid

    def form_valid(self, form):
        success = True

        email = form.cleaned_data['email']

        # If email suffix whitelist was setup
        if self.allowed_suffixes:
            email_valid = self.validate_email(email, self.allowed_suffixes)
            if not email_valid:
                form.add_error('email', 'Email is not at an allowed url')
                success = False

        if success:
            # Save inactive user
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Send Activation Email
            token = self.registration_backend.get_token(user)
            self.registration_backend.send_email(
                user,
                self.activation_subject,
                self.activation_body,
                token=token
            )

            # Show message
            return self.render_to_response(
                {'message': 'Success, an activation link has been sent to your email. Follow the link to continue'}
            )
        else:
            return self.form_invalid()

class SignupActivateView(TemplateView):

    template_name = "aristotle_mdr/users_management/self_invite.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registration_backend = BaseBackend()
        self.token_generator = RegistrationTokenGenerator()
        self.user_model = get_user_model()

        self.error_redirect = reverse('friendly_login')
        self.success_redirect = reverse('friendly_login') + '?welcome=true'

    def dispatch(self, request, *args, **kwargs):
        aristotle_settings = fetch_aristotle_settings()

        try:
            signup_settings = aristotle_settings['registry']['SELF_SIGNUP']
        except KeyError:
            return self.signup_disabled_message()

        if not signup_settings.get('enabled', False):
            return self.signup_disabled_message()

        return super().dispatch(request, *args, **kwargs)

    def signup_disbaled_message(self):
        return self.render_to_response({'message': 'Self Signup is not enabled'})

    def get(self, request, *args, **kwargs):

        user_id = self.kwargs.get('user_id', None)
        token = self.kwargs.get('token', None)

        if not user_id or not token:
            return HttpResponseRedirect(self.error_redirect)

        try:
            user = self.user_model.objects.get(id=user_id, is_active=False)
        except self.user_model.DoesNotExist:
            return HttpResponseRedirect(self.error_redirect)

        if self.token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponseRedirect(self.success_redirect)
        else:
            return HttpResponseRedirect(self.error_redirect)






