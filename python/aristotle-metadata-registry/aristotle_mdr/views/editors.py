from django.db import transaction
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView, DetailView, UpdateView
)

import reversion

from aristotle_mdr.utils import (
    concept_to_clone_dict,
    construct_change_message, url_slugify_concept, is_active_module,
    get_m2m_through
)
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR

from aristotle_mdr.views.utils import ObjectLevelPermissionRequiredMixin
from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier
from aristotle_mdr.contrib.slots.models import Slot

import logging

from aristotle_mdr.contrib.generic.forms import (
    one_to_many_formset_factory, one_to_many_formset_save,
    one_to_many_formset_excludes, one_to_many_formset_filters,
    through_formset_factory, ordered_formset_save,
    get_weak_formset, get_order_formset
)
import re

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class ConceptEditFormView(ObjectLevelPermissionRequiredMixin):
    raise_exception = True
    redirect_unauthenticated_users = True
    object_level_permissions = True
    model = MDR._concept
    pk_url_kwarg = 'iid'

    def dispatch(self, request, *args, **kwargs):
        self.item = super().get_object().item
        self.model = self.item.__class__
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'model': self.model._meta.model_name,
                        'app_label': self.model._meta.app_label,
                        'item': self.item})
        return context


class EditItemView(ConceptEditFormView, UpdateView):
    template_name = "aristotle_mdr/actions/advanced_editor.html"
    permission_required = "aristotle_mdr.user_can_edit"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slots_active = is_active_module('aristotle_mdr.contrib.slots')
        self.identifiers_active = is_active_module('aristotle_mdr.contrib.identifiers')

    def get_form_class(self):
        return MDRForms.wizards.subclassed_edit_modelform(self.model)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'instance': self.item,
        })
        return kwargs

    def get_extra_formsets(self, postdata=None):

        extra_formsets = []
        if self.slots_active:
            slot_formset = self.get_slots_formset()(
                queryset=Slot.objects.filter(concept=self.item.id),
                instance=self.item.concept,
                data=postdata
            )

            extra_formsets.append({
                'formset': slot_formset,
                'type': 'slot',
                'saveargs': None
            })

        if self.identifiers_active:
            id_formset = self.get_identifier_formset()(
                queryset=ScopedIdentifier.objects.filter(concept=self.item.id),
                instance=self.item.concept,
                data=postdata
            )

            extra_formsets.append({
                'formset': id_formset,
                'type': 'identifiers',
                'saveargs': None
            })

        if (hasattr(self.item, 'serialize_weak_entities')):
            # if weak formset is active
            weak = self.item.serialize_weak_entities

            for entity in weak:
                queryset = getattr(self.item, entity[1]).all()
                formset_info = self.get_weak_formset(entity, queryset=queryset, postdata=postdata)
                weak_formset = formset_info['formset']

                title = 'Edit ' + queryset.model.__name__
                # add spaces before capital letters
                title = re.sub(r"\B([A-Z])", r" \1", title)

                extra_formsets.append({
                    'formset': weak_formset,
                    'type': 'weak',
                    'title': title,
                    'saveargs': {
                        'formset': weak_formset,
                        'item': self.item,
                        'model_to_add_field': formset_info['model_field'],
                        'ordering_field': formset_info['ordering']
                    }
                })

        through_list = get_m2m_through(self.item)
        for through in through_list:
            formset = self.get_order_formset(through, postdata)
            extra_formsets.append({
                'formset': formset,
                'type': 'through',
                'title': through['field_name'].title(),
                'saveargs': {
                    'formset': formset,
                    'item': self.item,
                    'model_to_add_field': through['item_fields'][0],
                    'ordering_field': 'order'
                }
            })

        return extra_formsets

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        extra_formsets = self.get_extra_formsets(postdata=request.POST)

        self.object = self.item

        invalid = False

        if form.is_valid():
            item = form.save(commit=False)
            has_change_comments = form.data.get('change_comments', False)
            change_comments = form.data.get('change_comments', "")
        else:
            invalid = True


        for formsetinfo in extra_formsets:

            if not formsetinfo['formset'].is_valid():
                invalid = True

        if invalid:
            return self.form_invalid(form, formsets=formsets_to_save)
        else:
            with transaction.atomic(), reversion.revisions.create_revision():

                # Save formsets
                for formsetinfo in extra_formsets:
                    if formsetinfo['saveargs']:
                        ordered_formset_save(**formsetinfo['saveargs'])
                    else:
                        formsetinfo['formset'].save()

                # save the change comments
                # if not has_change_comments:
                #     change_comments += construct_change_message(request, form, changed_formsets)

                reversion.revisions.set_user(request.user)
                reversion.revisions.set_comment(change_comments)

                # Save item
                form.save_m2m()
                item.save()

            return HttpResponseRedirect(url_slugify_concept(self.item))

    def get_slots_formset(self):
        from aristotle_mdr.contrib.slots.forms import slot_inlineformset_factory
        return slot_inlineformset_factory(model=self.model)

    def get_identifier_formset(self):
        from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier

        return inlineformset_factory(
            MDR._concept, ScopedIdentifier,
            can_delete=True,
            fields=('concept', 'namespace', 'identifier', 'version'),
            extra=1,
            )

    def get_weak_formset(self, entity, postdata=None, queryset=None):
        return get_weak_formset(entity, self.model, item=self.item, postdata=postdata, queryset=queryset)

    def get_order_formset(self, through, postdata=None):
        return get_order_formset(through, self.item, postdata)

    def form_invalid(self, form, formsets=None):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """

        return self.render_to_response(self.get_context_data(form=form, formsets=formsets))

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)

        if 'formsets' in kwargs:
            extra_formsets = kwargs['formsets']
        else:
            extra_formsets = self.get_extra_formsets()

        for formsetinfo in extra_formsets:
            type = formsetinfo['type']
            if type == 'identifiers':
                context['identifier_FormSet'] = formsetinfo['formset']
            elif type == 'slot':
                context['slots_FormSet'] = formsetinfo['formset']
            elif type == 'weak':
                if 'weak_formsets' not in context.keys():
                    context['weak_formsets'] = []
                context['weak_formsets'].append({'formset': formsetinfo['formset'], 'title': formsetinfo['title']})
            elif type == 'through':
                if 'through_formsets' not in context.keys():
                    context['through_formsets'] = []
                context['through_formsets'].append({'formset': formsetinfo['formset'], 'title': formsetinfo['title']})

        context['show_slots_tab'] = self.slots_active
        context['show_id_tab'] = self.identifiers_active

        return context


class CloneItemView(ConceptEditFormView, DetailView, CreateView):
    template_name = "aristotle_mdr/create/clone_item.html"
    permission_required = "aristotle_mdr.user_can_view"

    def get_form_class(self):
        return MDRForms.wizards.subclassed_clone_modelform(self.model)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'initial': concept_to_clone_dict(self.item)
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                new_clone = form.save(commit=False)
                new_clone.submitter = self.request.user
                new_clone.save()
                reversion.revisions.set_user(self.request.user)
                reversion.revisions.set_comment("Cloned from %s (id: %s)" % (self.item.name, str(self.item.pk)))
                return HttpResponseRedirect(url_slugify_concept(new_clone))
        else:
            return self.form_invalid(form)
