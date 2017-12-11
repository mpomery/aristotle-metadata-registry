from django import forms
from django.forms.widgets import (
    TextInput, CheckboxSelectMultiple, Input,
    RadioSelect
)

from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class NameSuggestInput(TextInput):
    def __init__(self, *args, **kwargs):
        self.suggest_fields = kwargs.pop('name_suggest_fields')
        self.separator = kwargs.pop('separator', '-')
        super(NameSuggestInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        out = super().render(name, value, attrs)
        if self.suggest_fields:
            button = u"<button type='button' data-separator='{}' data-suggest-fields='{}'>Suggest</button>".format(self.separator, ",".join(self.suggest_fields))
            out = u"<div class='suggest_name_wrapper'>{}{}</div>".format(out, button)
        return mark_safe(out)


# Thanks http://stackoverflow.com/questions/6727372/
class RegistrationAuthoritySelect(forms.Select):
    def render(self, name, value, **kwargs):
        attrs = kwargs.get('attrs', None)
        if value is not None:
            attrs['disabled']='disabled'
            _id = attrs.get('id')
            # Insert a hidden field with the same name as 'disabled' fields aren't submitted.
            # http://stackoverflow.com/questions/368813/
            hidden_input_with_value = '<input type="hidden" id="%s" name="%s" value="%s" />' % (_id, name, value)
            attrs['id'] = _id + "_disabled"
            name = name + "_disabled"
            rendered = super().render(name, value, **kwargs)
            return mark_safe(rendered + hidden_input_with_value)
        else:
            return super().render(name, value, **kwargs)
