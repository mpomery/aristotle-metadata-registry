
from django import VERSION as django_version
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, RedirectView
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.contrib.contenttypes.models import ContentType
from formtools.wizard.views import SessionWizardView

import json
import copy

import reversion
from reversion_compare.views import HistoryCompareDetailView

from aristotle_mdr.perms import (
    user_can_view, user_can_edit,
    user_can_change_status
)
from aristotle_mdr import perms
from aristotle_mdr.utils import cache_per_item_user, url_slugify_concept
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR
from aristotle_mdr.utils import get_concepts_for_apps, fetch_aristotle_settings, fetch_aristotle_downloaders
from aristotle_mdr.views.utils import generate_visibility_matrix
from aristotle_mdr.contrib.slots.utils import get_allowed_slots

from haystack.views import FacetedSearchView

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

PAGES_PER_RELATED_ITEM = 15


class SmartRoot(RedirectView):
    unauthenticated_pattern = None
    authenticated_pattern = None

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            self.pattern_name = self.authenticated_pattern
        else:
            self.pattern_name = self.unauthenticated_pattern
        return super().get_redirect_url(*args, **kwargs)


class DynamicTemplateView(TemplateView):
    def get_template_names(self):
        return ['aristotle_mdr/static/%s.html' % self.kwargs['template']]


class ConceptHistoryCompareView(HistoryCompareDetailView):
    model = MDR._concept
    pk_url_kwarg = 'iid'
    template_name = "aristotle_mdr/actions/concept_history_compare.html"

    def get_object(self, queryset=None):
        item = super().get_object(queryset)
        if not user_can_view(self.request.user, item):
            raise PermissionDenied
        self.model = item.item.__class__  # Get the subclassed object
        return item

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def notification_redirect(self, content_type, object_id):

    ct = ContentType.objects.get(id=content_type)
    model_class = ct.model_class()
    obj = model_class.objects.get(id=object_id)
    return HttpResponseRedirect(obj.get_absolute_url())


def get_if_user_can_view(objtype, user, iid):
    item = get_object_or_404(objtype, pk=iid)
    if user_can_view(user, item):
        return item
    else:
        return False


def render_if_user_can_view(item_type, request, *args, **kwargs):
    # request = kwargs.pop('request')
    return render_if_condition_met(
        request, user_can_view, item_type, *args, **kwargs
    )


@login_required
def render_if_user_can_edit(item_type, request, *args, **kwargs):
    request = kwargs.pop('request')
    return render_if_condition_met(
        request, user_can_edit, item_type, *args, **kwargs
    )


def concept_by_uuid(request, uuid):
    item = get_object_or_404(MDR._concept, uuid=uuid)
    return redirect(url_slugify_concept(item))


def concept(*args, **kwargs):
    return render_if_user_can_view(MDR._concept, *args, **kwargs)


def measure(request, iid, model_slug, name_slug):
    item = get_object_or_404(MDR.Measure, pk=iid).item
    return render(
        request, [item.template],
        {
            'item': item,
            # 'view': request.GET.get('view', '').lower(),
            # 'last_edit': last_edit
        }
    )

    # return render_if_user_can_view(MDR.Measure, *args, **kwargs)


@cache_per_item_user(ttl=300, cache_post=False)
def render_if_condition_met(request, condition, objtype, iid, model_slug=None, name_slug=None, subpage=None):
    item = get_object_or_404(objtype, pk=iid).item
    if item._meta.model_name != model_slug or not slugify(item.name).startswith(str(name_slug)):
        return redirect(url_slugify_concept(item))
    if not condition(request.user, item):
        if request.user.is_anonymous():
            return redirect(
                reverse('friendly_login') + '?next=%s' % request.path
            )
        else:
            raise PermissionDenied

    # We add a user_can_edit flag in addition
    # to others as we have odd rules around who can edit objects.
    isFavourite = request.user.is_authenticated() and request.user.profile.is_favourite(item)
    from reversion.models import Version
    last_edit = Version.objects.get_for_object(item).first()

    # Only display viewable slots
    slots = get_allowed_slots(item, request.user)

    default_template = "%s/concepts/%s.html" % (item.__class__._meta.app_label, item.__class__._meta.model_name)
    return render(
        request, [default_template, item.template],
        {
            'item': item,
            'slots': slots,
            # 'view': request.GET.get('view', '').lower(),
            'isFavourite': isFavourite,
            'last_edit': last_edit
        }
    )


def registrationHistory(request, iid):
    item = get_if_user_can_view(MDR._concept, request.user, iid)
    if not item:
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied

    history = item.statuses.order_by("registrationAuthority", "-registrationDate")
    out = {}
    for status in history:
        if status.registrationAuthority in out.keys():
            out[status.registrationAuthority].append(status)
        else:
            out[status.registrationAuthority] = [status]

    return render(request, "aristotle_mdr/registrationHistory.html", {'item': item, 'history': out})


def unauthorised(request, path=''):
    if request.user.is_anonymous():
        return render(request, "401.html", {"path": path, "anon": True, }, status=401)
    else:
        return render(request, "403.html", {"path": path, "anon": True, }, status=403)


def create_list(request):
    if request.user.is_anonymous():
        return redirect(reverse('friendly_login') + '?next=%s' % request.path)
    if not perms.user_is_editor(request.user):
        raise PermissionDenied

    aristotle_apps = fetch_aristotle_settings().get('CONTENT_EXTENSIONS', [])
    aristotle_apps += ["aristotle_mdr"]
    out = {}

    wizards = []
    for wiz in getattr(settings, 'ARISTOTLE_SETTINGS', {}).get('METADATA_CREATION_WIZARDS', []):
        w = wiz.copy()
        _w = {
            'model': apps.get_app_config(wiz['app_label']).get_model(wiz['model']),
            'class': import_string(wiz['class']),
        }
        w.update(_w)
        wizards.append(w)

    for m in get_concepts_for_apps(aristotle_apps):
        # Only output subclasses of 11179 concept
        app_models = out.get(m.app_label, {'app': None, 'models': []})
        if app_models['app'] is None:
            try:
                app_models['app'] = getattr(apps.get_app_config(m.app_label), 'verbose_name')
            except:
                app_models['app'] = "No name"  # Where no name is configured in the app_config, set a dummy so we don't keep trying
        app_models['models'].append((m, m.model_class()))
        out[m.app_label] = app_models

    return render(
        request, "aristotle_mdr/create/create_list.html",
        {
            'models': sorted(out.values(), key=lambda x: x['app']),
            'wizards': wizards
        }
    )


@login_required
def toggleFavourite(request, iid):
    item = get_object_or_404(MDR._concept, pk=iid).item
    if not user_can_view(request.user, item):
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied
    request.user.profile.toggleFavourite(item)
    if request.GET.get('next', None):
        return redirect(request.GET.get('next'))
    if item.concept in request.user.profile.favourites.all():
        message = _("%s added to favourites.") % (item.name)
    else:
        message = _("%s removed from favourites.") % (item.name)
    message = _(message + " Review your favourites from the user menu.")
    messages.add_message(request, messages.SUCCESS, message)
    return redirect(url_slugify_concept(item))


# Actions

def display_review(wizard):
    if wizard.display_review is not None:
        return wizard.display_review
    else:
        return True


class ReviewChangesView(SessionWizardView):

    items = None
    display_review = None

    # Override this
    change_step_name = None

    def get_form_kwargs(self, step):

        if step == 'review_changes':
            items = self.get_items()
            # Check some values from last step
            cleaned_data = self.get_change_data()
            cascade = cleaned_data['cascadeRegistration']
            state = cleaned_data['state']
            ra = cleaned_data['registrationAuthorities']

            static_content = {'new_state': str(MDR.STATES[state]), 'new_reg_date': cleaned_data['registrationDate']}
            # Need to check wether cascaded was true here

            if cascade == 1:
                all_ids = []
                for item in items:

                    # Can't cascade from _concept
                    if isinstance(item, MDR._concept):
                        cascade = item.item.registry_cascade_items
                    else:
                        cascade = item.registry_cascade_items

                    cascaded_ids = [a.id for a in cascade]
                    cascaded_ids.append(item.id)
                    all_ids.extend(cascaded_ids)

                queryset = MDR._concept.objects.filter(id__in=all_ids)
            else:
                ids = [a.id for a in items]
                queryset = MDR._concept.objects.filter(id__in=ids)

            return {'queryset': queryset, 'static_content': static_content, 'ra': ra[0], 'user': self.request.user}

        return {}

    def get_form(self, step=None, data=None, files=None):

        self.set_review_var(step, data, files, self.change_step_name)
        return super().get_form(step, data, files)

    def get_change_data(self):
        # We override this when the change_data doesnt come form a form
        return self.get_cleaned_data_for_step(self.change_step_name)

    def set_review_var(self, step, data, files, change_step):

        # Set step if it's None
        if step is None:
            step = self.steps.current

        if step == change_step and data:
            review = True
            if data.get('submit_next'):
                review = True
            elif data.get('submit_skip'):
                review = False

            self.display_review = review

    def get_items(self):
        return self.items

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        if self.steps.current == 'review_changes':
            data = self.get_cleaned_data_for_step(self.change_step_name)
            if 'registrationAuthorities' in data:
                context.update({'ra': data['registrationAuthorities'][0]})

        return context

    def register_changes(self, form_dict, change_form=None, **kwargs):

        items = self.get_items()

        try:
            review_data = form_dict['review_changes'].cleaned_data
        except KeyError:
            review_data = None

        if review_data:
            selected_list = review_data['selected_list']

        # process the data in form.cleaned_data as required
        if change_form:
            cleaned_data = form_dict[change_form].cleaned_data
        else:
            cleaned_data = self.get_change_data(register=True)

        ras = cleaned_data['registrationAuthorities']
        state = cleaned_data['state']
        regDate = cleaned_data['registrationDate']
        cascade = cleaned_data['cascadeRegistration']
        changeDetails = cleaned_data['changeDetails']

        if changeDetails is None:
            changeDetails = ""

        success = []
        failed = []

        arguments = {
            'state': state,
            'user': self.request.user,
            'changeDetails': changeDetails,
            'registrationDate': regDate,
        }

        if review_data:
            for ra in ras:
                arguments['items'] = selected_list
                status = ra.register_many(**arguments)
                success.extend(status['success'])
                failed.extend(status['failed'])
        else:
            for item in items:
                for ra in ras:
                    # Should only be 1 ra
                    # Need to check before enforcing

                    # Can't cascade from _concept
                    if isinstance(item, MDR._concept):
                        arguments['item'] = item.item
                    else:
                        arguments['item'] = item

                    if cascade:
                        register_method = ra.cascaded_register
                    else:
                        register_method = ra.register

                    status = register_method(**arguments)
                    success.extend(status['success'])
                    failed.extend(status['failed'])

        return (success, failed)

    def register_changes_with_message(self, form_dict, change_form=None, *args, **kwargs):

        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.request.user)

            success, failed = self.register_changes(form_dict, change_form)

            bad_items = sorted([str(i.id) for i in failed])
            count = self.get_items().count()

            if failed:
                message = _(
                    "%(num_items)s items registered \n"
                    "%(num_faileds)s items failed, they had the id's: %(bad_ids)s"
                ) % {
                    'num_items': count,
                    'num_faileds': len(failed),
                    'bad_ids': ",".join(bad_items)
                }
            else:
                message = _(
                    "%(num_items)s items registered\n"
                ) % {
                    'num_items': count,
                }

            reversion.revisions.set_comment(message)

        return message


class ChangeStatusView(ReviewChangesView):

    change_step_name = 'change_status'

    form_list = [
        ('change_status', MDRForms.ChangeStatusForm),
        ('review_changes', MDRForms.ReviewChangesForm)
    ]

    templates = {
        'change_status': 'aristotle_mdr/actions/changeStatus.html',
        'review_changes': 'aristotle_mdr/actions/review_state_changes.html'
    }

    condition_dict = {'review_changes': display_review}

    display_review = None

    def dispatch(self, request, *args, **kwargs):
        # Check for keyError here
        self.item = get_object_or_404(MDR._concept, pk=kwargs['iid']).item

        if not (self.item and user_can_change_status(request.user, self.item)):
            if request.user.is_anonymous():
                return redirect(reverse('friendly_login') + '?next=%s' % request.path)
            else:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_items(self):
        return [self.item]

    def get_form_kwargs(self, step):

        kwargs = super().get_form_kwargs(step)

        if step == 'change_status':
            return {'user': self.request.user}

        return kwargs

    def get_context_data(self, form, **kwargs):
        item = self.item
        status_matrix = json.dumps(generate_visibility_matrix(self.request.user))
        context = super().get_context_data(form, **kwargs)
        context.update({'item': item, 'status_matrix': status_matrix})
        return context

    def done(self, form_list, form_dict, **kwargs):
        self.register_changes(form_dict, 'change_status')
        return HttpResponseRedirect(url_slugify_concept(self.item))


def supersede(request, iid):
    item = get_object_or_404(MDR._concept, pk=iid).item
    if not (item and user_can_edit(request.user, item)):
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied
    qs=item.__class__.objects.all()
    if request.method == 'POST':  # If the form has been submitted...
        form = MDRForms.SupersedeForm(request.POST, user=request.user, item=item, qs=qs)  # A form bound to the POST data
        if form.is_valid():
            with transaction.atomic(), reversion.revisions.create_revision():
                reversion.revisions.set_user(request.user)
                item.superseded_by = form.cleaned_data['newerItem']
                item.save()
            return HttpResponseRedirect(url_slugify_concept(item))
    else:
        form = MDRForms.SupersedeForm(item=item, user=request.user, qs=qs)
    return render(request, "aristotle_mdr/actions/supersedeItem.html", {"item": item, "form": form})


def deprecate(request, iid):
    item = get_object_or_404(MDR._concept, pk=iid).item
    if not (item and user_can_edit(request.user, item)):
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied
    qs=item.__class__.objects.filter().editable(request.user)
    if request.method == 'POST':  # If the form has been submitted...
        form = MDRForms.DeprecateForm(request.POST, user=request.user, item=item, qs=qs)  # A form bound to the POST data
        if form.is_valid():
            # Check use the itemset as there are permissions issues and we want to remove some:
            #  Everything that was superseded, but isn't in the returned set
            #  Everything that was in the returned set, but isn't already superseded
            #  Everything left over can stay the same, as its already superseded
            #    or wasn't superseded and is staying that way.
            with transaction.atomic(), reversion.revisions.create_revision():
                reversion.revisions.set_user(request.user)
                for i in item.supersedes.all():
                    if i not in form.cleaned_data['olderItems'] and user_can_edit(request.user, i):
                        item.supersedes.remove(i)
                for i in form.cleaned_data['olderItems']:
                    if user_can_edit(request.user, i):  # Would check item.supersedes but its a set
                        kwargs = {}
                        if django_version > (1, 9):
                            kwargs = {'bulk': False}
                        item.supersedes.add(i, **kwargs)
            return HttpResponseRedirect(url_slugify_concept(item))
    else:
        form = MDRForms.DeprecateForm(user=request.user, item=item, qs=qs)
    return render(request, "aristotle_mdr/actions/deprecateItems.html", {"item": item, "form": form})


def extensions(request):
    content=[]
    aristotle_apps = fetch_aristotle_settings().get('CONTENT_EXTENSIONS', [])

    if aristotle_apps:
        for app_label in aristotle_apps:
            app=apps.get_app_config(app_label)
            try:
                app.about_url = reverse('%s:about' % app_label)
            except:
                pass  # if there is no about URL, thats ok.
            content.append(app)

    content = list(set(content))
    aristotle_downloads = fetch_aristotle_downloaders()
    downloads=[]
    if aristotle_downloads:
        for download in aristotle_downloads:
            downloads.append(download())

    return render(
        request,
        "aristotle_mdr/static/extensions.html",
        {'content_extensions': content, 'download_extensions': downloads, }
    )


# Search views

class PermissionSearchView(FacetedSearchView):

    results_per_page_values = getattr(settings, 'RESULTS_PER_PAGE', [])

    def build_page(self):

        try:
            rpp = self.form.cleaned_data['rpp']
        except (AttributeError, KeyError):
            rpp = ''

        if rpp in self.results_per_page_values:
            self.results_per_page = rpp
        else:
            if len(self.results_per_page_values) > 0:
                self.results_per_page = self.results_per_page_values[0]

        return super().build_page()

    def build_form(self):

        form = super().build_form()
        form.request = self.request
        form.request.GET = self.clean_facets(self.request)
        return form

    def clean_facets(self, request):
        get = request.GET.copy()
        for k, val in get.items():
            if k.startswith('f__'):
                get.pop(k)
                k = k[4:]
                get.update({'f': '%s::%s' % (k, val)})
        return get

    def extra_context(self):
        # needed to compare to indexed primary key value
        if not self.request.user.is_anonymous():
            favourites_pks = self.request.user.profile.favourites.all().values_list('id', flat=True)
            favourites_list = list(favourites_pks)
        else:
            favourites_list = []

        return {'rpp_values': self.results_per_page_values, 'favourites': favourites_list}
