from django import forms
from django.forms.widgets import (
    TextInput, CheckboxSelectMultiple, Input,
    # ChoiceInput,
    # CheckboxChoiceInput,
    RadioSelect
)

from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from bootstrap3_datetime.widgets import DateTimePicker


class NameSuggestInput(TextInput):
    def __init__(self, *args, **kwargs):
        self.suggest_fields = kwargs.pop('name_suggest_fields')
        self.separator = kwargs.pop('separator', '-')
        super(NameSuggestInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        out = super(NameSuggestInput, self).render(name, value, attrs)
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
            rendered = super(RegistrationAuthoritySelect, self).render(name, value, **kwargs)
            return mark_safe(rendered + hidden_input_with_value)
        else:
            return super(RegistrationAuthoritySelect, self).render(name, value, **kwargs)


class BootstrapDateTimePicker(DateTimePicker):
    class Media:
        css = {
            'all': ('bootstrap3_datetime/bootstrap-datetimepicker.min.css',)
        }
        js = (
            'bootstrap3_datetime/moment.min.js',
            'bootstrap3_datetime/bootstrap-datetimepicker.min.js'
        )


class BootstrapDropdownSelect(RadioSelect):
    allow_multiple_selected = False
    template_name = "search/forms/widgets/radio.html"
    option_template_name = 'search/forms/widgets/radio_option.html'


class BootstrapDropdownIntelligentDate(BootstrapDropdownSelect):
    template_name = "search/forms/widgets/radio_and_date.html"
    option_template_name = 'search/forms/widgets/radio_option.html'


class BootstrapDropdownSelectMultiple(CheckboxSelectMultiple):
    allow_multiple_selected = True
    template_name = "search/forms/widgets/radio.html"
    option_template_name = 'search/forms/widgets/checkbox_option.html'
