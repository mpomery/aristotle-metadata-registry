from django.http import HttpResponseRedirect

from aristotle_mdr.contrib.generic.views import GenericWithItemURLFormView
from aristotle_mdr.contrib.self_publish.forms import MetadataPublishForm
from aristotle_mdr.contrib.self_publish.models import PublicationRecord


def is_submitter_or_super(user, item):
    return user.is_superuser or user == item.submitter


class PublishMetadataFormView(GenericWithItemURLFormView):
    permission_checks = [is_submitter_or_super]
    template_name = "aristotle_self_publish/publish_metadata.html"
    form_class = MetadataPublishForm

    def form_valid(self, form):
        defaults={
            'visibility': form.cleaned_data['visibility'],
            'note': form.cleaned_data['note'],
            'publication_date': form.cleaned_data['publication_date']
        }
        rec, c = PublicationRecord.objects.update_or_create(
            concept=self.item,
            user=self.request.user,
            defaults=defaults
        )
        return HttpResponseRedirect(self.get_success_url())
