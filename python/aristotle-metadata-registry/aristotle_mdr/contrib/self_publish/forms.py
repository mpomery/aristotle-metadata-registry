from django.forms import ModelForm
from aristotle_mdr.contrib.self_publish.models import PublicationRecord
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
from django.forms import RadioSelect


class MetadataPublishForm(ModelForm):
    class Meta:
        model = PublicationRecord
        exclude = ('user', 'concept')
        widgets = {
            'publication_date': BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
            'visibility': RadioSelect()
        }
