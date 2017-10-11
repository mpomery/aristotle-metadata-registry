from organizations.backends.defaults import BaseBackend
from organizations.backends.forms import UserRegistrationForm


class NewuserOnlyRegistrationBackend(BaseBackend):
    """
    A backend for allowing new users to join the site by creating a new user
    associated with a new organization.
    """
    # NOTE this backend stands to be simplified further, as email verification
    # should be beyond the purview of this app
    activation_subject = 'organizations/email/activation_subject.txt'
    activation_body = 'organizations/email/activation_body.html'
    reminder_subject = 'organizations/email/reminder_subject.txt'
    reminder_body = 'organizations/email/reminder_body.html'
    form_class = UserRegistrationForm

    def get_success_url(self):
        return reverse('registration_success')

    def get_urls(self):
        return [
            url(r'^complete/$', view=self.success_view,
                name="registration_success"),
            url(r'^(?P<user_id>[\d]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                view=self.activate_view, name="registration_register"),
            url(r'^$', view=self.create_view, name="registration_create"),
        ]

    def register_by_email(self, email, sender=None, request=None, **kwargs):
        """
        Returns a User object filled with dummy data and not active, and sends
        an invitation email.
        """
        try:
            user = self.user_model.objects.get(email=email)
        except self.user_model.DoesNotExist:
            user = self.user_model.objects.create(username=self.get_username(),
                    email=email, password=self.user_model.objects.make_random_password())
            user.is_active = False
            user.save()
        self.send_activation(user, sender, **kwargs)
        return user

    def send_activation(self, user, sender=None, **kwargs):
        """
        Invites a user to join the site
        """
        if user.is_active:
            return False
        token = self.get_token(user)
        kwargs.update({'token': token})
        self.email_message(user, self.activation_subject, self.activation_body, sender, **kwargs).send()

    def create_view(self, request):
        """
        Initiates the organization and user account creation process
        """
        if request.user.is_authenticated():
            return redirect("organization_add")
        form = org_registration_form(self.org_model)(request.POST or None)
        if form.is_valid():
            try:
                user = self.user_model.objects.get(email=form.cleaned_data['email'])
            except self.user_model.DoesNotExist:
                user = self.user_model.objects.create(username=self.get_username(),
                        email=form.cleaned_data['email'],
                        password=self.user_model.objects.make_random_password())
                user.is_active = False
                user.save()
            else:
                return redirect("organization_add")
            organization = create_organization(user, form.cleaned_data['name'],
                    form.cleaned_data['slug'], is_active=False)
            return render(request, self.activation_success_template, {'user': user, 'organization': organization})
        return render(request, self.registration_form_template, {'form': form})

    def success_view(self, request):
        return render(request, self.activation_success_template, {})
