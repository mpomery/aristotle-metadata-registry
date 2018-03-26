from django import forms
from django.forms.widgets import TextInput, CheckboxSelectMultiple

from django.utils.safestring import mark_safe


class NameSuggestInput(TextInput):
    def __init__(self, *args, **kwargs):
        self.suggest_fields = kwargs.pop('name_suggest_fields')
        self.separator = kwargs.pop('separator', '-')
        super().__init__(*args, **kwargs)

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


class TableCheckboxSelect(CheckboxSelectMultiple):

    def __init__(self, extra_info, static_info, headers, top_header, order, attrs=None, choices=(), **kwargs):
        super().__init__(attrs, choices, **kwargs)
        self.extra_info = extra_info
        self.static_info = static_info
        self.order = order
        self.header_list = []

        for field in order:
            header = headers[field]
            if header:
                self.header_list.append(header)

        self.top_header = top_header
        self.badperms = False

    template_name = 'aristotle_mdr/widgets/table_checkbox_select.html'
    option_template_name = 'aristotle_mdr/widgets/table_checkbox_option.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option_extra = self.extra_info[option['value']]
        option_extra_list = []

        for field in self.order:

            if field in ['input', 'label']:
                continue

            try:
                value = option_extra[field]
            except KeyError:
                value = None

            if not value:
                try:
                    value = self.static_info[field]
                except KeyError:
                    value = None

            option_extra_list.append(value)

        option['extra'] = option_extra_list
        option['permission'] = option_extra['perm']

        if not option['permission']:
            self.badperms = True

        return option

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        context.update({
            'static_info': self.static_info,
            'headers': self.header_list,
            'badperms': self.badperms,
            'top_header': self.top_header
        })

        return context
