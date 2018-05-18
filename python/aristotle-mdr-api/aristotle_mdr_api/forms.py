from django.forms import ModelForm, Form
from django_jsonforms.forms import JSONSchemaField

class TokenCreateForm(Form):

    json = JSONSchemaField(
        schema = 'aristotle_mdr_api/schema.json',
        options = {'theme': 'bootstrap3'}
    )
