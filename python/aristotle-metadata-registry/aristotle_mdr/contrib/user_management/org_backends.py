from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from django.conf.urls import url
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import FormView

from organizations.backends.defaults import InvitationBackend

from . import forms

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage
from django.utils.translation import ugettext_lazy as _

from django.http import Http404

import logging
logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class AristotleInvitationBackend(InvitationBackend):
    """
    A backend for allowing new users to join the site by creating a new user
    associated with a new organization.
    """

    form_class = forms.AristotleUserRegistrationForm

    def get_success_url(self):
        return reverse('invitation_success')

    def get_urls(self):
        return [
            # url(r'^accept/(?P<token>[0-9A-Za-z\-]{1,50})/$',
            url(r'^accept/(?P<token>.*)/$',
                view=self.activate_view, name="registry_invitations_register"),
            # url(r'^complete$', view=self.invite_view(), name="registry_invitations_complete"),
            url(r'^$', view=self.invite_view(), name="registry_invitations_create"),
        ]

    def invite_view(self):
        """
        Initiates the organization and user account creation process
        """
        return InviteView.as_view(backend=self)

    def success_view(self, request):
        return render(request, self.activation_success_template, {})

    def activate_view(self, request, token):
        """
        View function that activates the given User by setting `is_active` to
        true if the provided information is verified.
        """
        user = self.check_token(token)

        form = self.get_form(data=request.POST or None, instance=user)
        if form.is_valid():
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            self.activate_organizations(user)
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            login(request, user)
            self.delete_token(token)
            return redirect("/")  # self.get_success_url())
        return render(request, self.registration_form_template, {'form': form})

    def invite_by_emails(self, emails, sender=None, request=None, **kwargs):
        """Creates an inactive user with the information we know and then sends
        an invitation email for that user to complete registration.
        If your project uses email in a different way then you should make to
        extend this method as it only checks the `email` attribute for Users.
        """
        User = get_user_model()
        users = []
        for email in emails:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # TODO break out user creation process
                user = User.objects.create(
                    email=email,
                    password=get_user_model().objects.make_random_password()
                )
                user.is_active = False
                user.save()
            self.send_invitation(user, sender, request=request, **kwargs)
            users.append(user)
        return users

    def _get_token(self, user, message, **kwargs):
        """Returns a unique token for the given user"""
        from django.core.cache import caches
        import uuid
        cache = caches['aristotle-mdr-invitations']
        token = str(uuid.uuid4())
        cache.set(token, message)
        return token

    def delete_token(self, token):
        from django.core.cache import caches
        cache = caches['aristotle-mdr-invitations']
        cache.delete(token)

    def email_message(self, user, subject_template, body_template, request, sender=None, message_class=EmailMessage, **kwargs):
        """
        Returns an email message for a new user. This can be easily overriden.
        For instance, to send an HTML message, use the EmailMultiAlternatives message_class
        and attach the additional conent.
        """

        if sender:
            import email.utils
            from_email = "%s %s <%s>" % (
                sender.first_name, sender.last_name,
                email.utils.parseaddr(settings.DEFAULT_FROM_EMAIL)[1]
            )
            reply_to = "%s %s <%s>" % (sender.first_name, sender.last_name, sender.email)
        else:
            from_email = settings.DEFAULT_FROM_EMAIL
            reply_to = from_email

        headers = {'Reply-To': reply_to}
        kwargs.update({'sender': sender, 'user': user})

        subject = render(request, subject_template, kwargs)  # .strip()  # Remove stray newline characters
        body = render(request, body_template, kwargs)
        logger.info("UserInvited: {email} invited to registry by {inv_email}".format(email=user.email, inv_email=request.user.email))
        return message_class(subject, body, from_email, [user.email], headers=headers)

    def send_invitation(self, user, sender=None, **kwargs):
        """An intermediary function for sending an invitation email that
        selects the templates, generating the token, and ensuring that the user
        has not already joined the site.
        """
        if user.is_active:
            return False
        token = self.get_token(user)
        kwargs.update({'token': token})
        kwargs.update({'sender': sender})
        self.email_message(user, self.invitation_subject, self.invitation_body, **kwargs).send()
        return True


class NewUserInvitationBackend(AristotleInvitationBackend):

    notification_subject = 'aristotle_mdr/users_management/newuser/email/notification_subject.txt'
    notification_body = 'aristotle_mdr/users_management/newuser/email/notification_body.html'
    invitation_subject = 'aristotle_mdr/users_management/newuser/email/invitation_subject.txt'
    invitation_body = 'aristotle_mdr/users_management/newuser/email/invitation_body.html'
    reminder_subject = 'aristotle_mdr/users_management/newuser/email/reminder_subject.txt'
    reminder_body = 'aristotle_mdr/users_management/newuser/email/reminder_body.html'

    registration_form_template = 'aristotle_mdr/users_management/newuser/register_form.html'
    activation_success_template = 'aristotle_mdr/users_management/newuser/register_success.html'

    def get_token(self, user, **kwargs):
        message = {'user_email': user.email, 'invited_to': "__registry__"}
        return self._get_token(user, message)

    def check_token(self, token):
        from django.core.cache import caches
        cache = caches['aristotle-mdr-invitations']
        obj = cache.get(token)

        if not obj or obj.get('invited_to') != "__registry__" or 'user_email' not in obj.keys():
            raise Http404(_("Your invitation may have expired."))

        try:
            user = get_user_model().objects.get(email=obj.get('user_email'), is_active=False)
        except get_user_model().DoesNotExist:
            raise Http404(_("Your URL may have expired."))

        return user


class InviteView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = forms.UserInvitationForm
    template_name = "aristotle_mdr/users_management/invite_user_to_registry.html"
    backend = None
    success_url = "aristotle-user:registry_user_list"

    permission_required = "aristotle_mdr.invite_users_to_registry"
    raise_exception = True
    redirect_unauthenticated_users = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        self.backend.invite_by_emails(form.emails, request=self.request)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(self.success_url)
