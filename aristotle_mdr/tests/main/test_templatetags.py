from django.template import Context, Template
from django.test import TestCase

import aristotle_mdr.models as models

from django.core.exceptions import FieldDoesNotExist
from django.template.exceptions import TemplateSyntaxError

# Execute in a test environment.
from aristotle_mdr.utils import setup_aristotle_test_environment

setup_aristotle_test_environment()


preamble = "{% load aristotle_tags %}"


class TestTemplateTags_aristotle_tags_py(TestCase):
    def setUp(self):
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA")
        self.wg = models.Workgroup.objects.create(name="Test WG 1")
        self.wg.registrationAuthorities=[self.ra]
        self.wg.save()
        self.item = models.ObjectClass.objects.create(name="Test OC1", workgroup=self.wg)

    def test_doc(self):
        context = Context({"item": self.item})

        # Definition has helptext
        template = Template(preamble + "{% doc item 'definition' %}")
        template = template.render(context)
        self.assertTrue('Representation of a concept by a descriptive statement' in template)

        # Modified does not (it comes from django-model-utils
        template = Template(preamble + "{% doc item 'modified' %}")
        template = template.render(context)
        self.assertTrue('No help text for the field' in template)

        template = Template(preamble + "{% doc item %}")
        template.render(context)

        with self.assertRaises(FieldDoesNotExist):
            template = Template(preamble + "{% doc item 'not_an_attribute' %}")
            template.render(context)

    def use_safe_filter(self, safefilter):
        context = Context({"item": self.item})

        template = Template(preamble + "{{ 'comment'|%s:'user' }}" % (safefilter))
        page = template.render(context).replace('\n', '').strip()
        self.assertEqual(page, 'False')

        with self.assertRaises(TemplateSyntaxError):
            template = Template(preamble + "{{ 'comment'|%s }}" % (safefilter))
            template.render(context)

    def test_can_alter_comment(self):
        self.use_safe_filter('can_alter_comment')

    def test_can_alter_post(self):
        self.use_safe_filter('can_alter_post')

    def test_in_workgroup(self):
        self.use_safe_filter('in_workgroup')
