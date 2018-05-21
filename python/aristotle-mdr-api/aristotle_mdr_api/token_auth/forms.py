from django.forms import ModelForm, Form
from django.forms.fields import CharField
from django_jsonforms.forms import JSONSchemaField

class TokenCreateForm(Form):

    name = CharField(max_length=100)
    perm_json = JSONSchemaField(
        schema = 'aristotle_mdr_api/schema.json',
        options = {
            'theme': 'bootstrap3',
            'disable_properties': True,
            'disable_collapse': True,
            'disable_edit_json': True,
            'no_additional_properties': True
        },
        label=''
    )
