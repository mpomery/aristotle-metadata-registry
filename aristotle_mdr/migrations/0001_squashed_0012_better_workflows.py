# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import model_utils.fields
import ckeditor.fields
import django.utils.timezone
from django.conf import settings
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    replaces = [('aristotle_mdr', '0001_initial'), ('aristotle_mdr', '0002_auto_20150409_0656'), ('aristotle_mdr', '0003_auto_20150416_0024'), ('aristotle_mdr', '0004_auto_20150424_0059'), ('aristotle_mdr', '0005_auto_20150526_1058'), ('aristotle_mdr', '0006_remove_status_indictionary'), ('aristotle_mdr', '0007_rename_description_fields'), ('aristotle_mdr', '0008_auto_20151216_0339'), ('aristotle_mdr', '0009_add_explicit_related_name_for_values'), ('aristotle_mdr', '0010_auto_20160106_1814'), ('aristotle_mdr', '0011_update_ckeditor_remove_d19_errors'), ('aristotle_mdr', '0012_better_workflows')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='_concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.TextField(help_text='The primary name used for human identification purposes.')),
                ('definition', ckeditor.fields.RichTextField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts', verbose_name='definition')),
                ('readyToReview', models.BooleanField(default=False)),
                ('_is_public', models.BooleanField(default=False)),
                ('_is_locked', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'item',
            },
        ),
        migrations.CreateModel(
            name='ConceptualDomain',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor.fields.RichTextField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor.fields.RichTextField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('value_description', models.TextField(help_text='Description or specification of a rule, reference, or range for a set of all value meanings for a Conceptual Domain', verbose_name='description', blank=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.ConceptualDomain', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='DataElement',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor.fields.RichTextField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor.fields.RichTextField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='DataElementConcept',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor.fields.RichTextField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor.fields.RichTextField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('conceptualDomain', models.ForeignKey(blank=True, to='aristotle_mdr.ConceptualDomain', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='DataElementDerivation',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('derivation_rule', models.TextField(blank=True)),
                ('derives', models.ForeignKey(related_name='derived_from', blank=True, to='aristotle_mdr.DataElement', null=True)),
                ('inputs', models.ManyToManyField(related_name='input_to_derivation', to='aristotle_mdr.DataElement', blank=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.DataElementDerivation', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor.fields.RichTextField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor.fields.RichTextField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.DataType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='DiscussionComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('body', models.TextField()),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='DiscussionPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('body', models.TextField()),
                ('title', models.CharField(max_length=256)),
                ('closed', models.BooleanField(default=False)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-modified'],
            },
        ),

        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.TextField(help_text='The primary name used for human identification purposes.')),
                ('description', ckeditor.fields.RichTextField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts', verbose_name='definition')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ObjectClass',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.ObjectClass', null=True)),
            ],
            options={
                'verbose_name_plural': 'Object Classes',
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='PermissibleValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=32)),
                ('meaning', models.CharField(max_length=255)),
                ('order', models.PositiveSmallIntegerField(verbose_name='Position')),
                ('start_date', models.DateField(help_text='Date at which the value became valid', null=True, blank=True)),
                ('end_date', models.DateField(help_text='Date at which the value ceased to be valid', null=True, blank=True)),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PossumProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.Property', null=True)),
            ],
            options={
                'verbose_name_plural': 'Properties',
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='RegistrationAuthority',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.TextField(help_text='The primary name used for human identification purposes.')),
                ('definition', ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts', verbose_name='definition')),
                ('locked_state', models.IntegerField(default=2, choices=[(0, 'Not Progressed'), (1, 'Incomplete'), (2, 'Candidate'), (3, 'Recorded'), (4, 'Qualified'), (5, 'Standard'), (6, 'Preferred Standard'), (7, 'Superseded'), (8, 'Retired')])),
                ('public_state', models.IntegerField(default=3, choices=[(0, 'Not Progressed'), (1, 'Incomplete'), (2, 'Candidate'), (3, 'Recorded'), (4, 'Qualified'), (5, 'Standard'), (6, 'Preferred Standard'), (7, 'Superseded'), (8, 'Retired')])),
                ('notprogressed', models.TextField(blank=True)),
                ('incomplete', models.TextField(blank=True)),
                ('candidate', models.TextField(blank=True)),
                ('recorded', models.TextField(blank=True)),
                ('qualified', models.TextField(blank=True)),
                ('standard', models.TextField(blank=True)),
                ('preferred', models.TextField(blank=True)),
                ('superseded', models.TextField(blank=True)),
                ('retired', models.TextField(blank=True)),
                ('managers', models.ManyToManyField(related_name='registrationauthority_manager_in', verbose_name='Managers', to=settings.AUTH_USER_MODEL, blank=True)),
                ('registrars', models.ManyToManyField(related_name='registrar_in', verbose_name='Registrars', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Registration Authorities',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('changeDetails', models.CharField(max_length=512, null=True, blank=True)),
                ('state', models.IntegerField(default=1, choices=[(0, 'Not Progressed'), (1, 'Incomplete'), (2, 'Candidate'), (3, 'Recorded'), (4, 'Qualified'), (5, 'Standard'), (6, 'Preferred Standard'), (7, 'Superseded'), (8, 'Retired')])),
                ('inDictionary', models.BooleanField(default=True)),
                ('registrationDate', models.DateField()),
            ],
            options={
                'verbose_name_plural': 'Statuses',
            },
        ),
        migrations.CreateModel(
            name='SupplementaryValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=32)),
                ('meaning', models.CharField(max_length=255)),
                ('order', models.PositiveSmallIntegerField(verbose_name='Position')),
                ('start_date', models.DateField(help_text='Date at which the value became valid', null=True, blank=True)),
                ('end_date', models.DateField(help_text='Date at which the value ceased to be valid', null=True, blank=True)),
            ],
            options={
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UnitOfMeasure',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor.fields.RichTextField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor.fields.RichTextField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('symbol', models.CharField(max_length=20, blank=True)),
                ('measure', models.ForeignKey(blank=True, to='aristotle_mdr.Measure', null=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.UnitOfMeasure', null=True)),
            ],
            options={
                'verbose_name_plural': 'Units Of Measure',
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='ValueDomain',
            fields=[
                ('_concept_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aristotle_mdr._concept')),
                ('short_name', models.CharField(max_length=100, blank=True)),
                ('version', models.CharField(max_length=20, blank=True)),
                ('synonyms', models.CharField(max_length=200, blank=True)),
                ('references', ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ('origin_URI', models.URLField(help_text='If imported, the original location of the item', blank=True)),
                ('comments', ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True)),
                ('submitting_organisation', models.CharField(max_length=256, blank=True)),
                ('responsible_organisation', models.CharField(max_length=256, blank=True)),
                ('format', models.CharField(max_length=100, null=True, blank=True)),
                ('maximum_length', models.PositiveIntegerField(null=True, blank=True)),
                ('description', models.TextField(help_text='Description or specification of a rule, reference, or range for a set of all values for a Value Domain.', verbose_name='description', blank=True)),
                ('conceptual_domain', models.ForeignKey(blank=True, to='aristotle_mdr.ConceptualDomain', null=True)),
                ('data_type', models.ForeignKey(blank=True, to='aristotle_mdr.DataType', null=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.ValueDomain', null=True)),
                ('unit_of_measure', models.ForeignKey(blank=True, to='aristotle_mdr.UnitOfMeasure', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('aristotle_mdr._concept',),
        ),
        migrations.CreateModel(
            name='ValueMeaning',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meaning', models.CharField(max_length=255)),
                ('order', models.PositiveSmallIntegerField(verbose_name='Position')),
                ('start_date', models.DateField(help_text='Date at which the value meaning became valid', null=True, blank=True)),
                ('end_date', models.DateField(help_text='Date at which the value meaning ceased to be valid', null=True, blank=True)),
                ('conceptual_domain', models.ForeignKey(to='aristotle_mdr.ConceptualDomain')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Workgroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.TextField(help_text='The primary name used for human identification purposes.')),
                ('definition', ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts', verbose_name='definition')),
                ('archived', models.BooleanField(default=False, help_text='Archived workgroups can no longer have new items or discussions created within them.', verbose_name='Archived')),
                ('managers', models.ManyToManyField(related_name='workgroup_manager_in', verbose_name='Managers', to=settings.AUTH_USER_MODEL, blank=True)),
                ('stewards', models.ManyToManyField(related_name='steward_in', verbose_name='Stewards', to=settings.AUTH_USER_MODEL, blank=True)),
                ('submitters', models.ManyToManyField(related_name='submitter_in', verbose_name='Submitters', to=settings.AUTH_USER_MODEL, blank=True)),
                ('viewers', models.ManyToManyField(related_name='viewer_in', verbose_name='Viewers', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='supplementaryvalue',
            name='valueDomain',
            field=models.ForeignKey(related_name='supplementaryvalue_set', to='aristotle_mdr.ValueDomain'),
        ),
        migrations.AddField(
            model_name='supplementaryvalue',
            name='value_meaning',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ValueMeaning', null=True),
        ),
        migrations.AddField(
            model_name='status',
            name='concept',
            field=models.ForeignKey(related_name='statuses', to='aristotle_mdr._concept'),
        ),
        migrations.AddField(
            model_name='status',
            name='registrationAuthority',
            field=models.ForeignKey(to='aristotle_mdr.RegistrationAuthority'),
        ),
        migrations.AlterUniqueTogether(
            name='status',
            unique_together=set([('concept', 'registrationAuthority')]),
        ),
        migrations.AddField(
            model_name='possumprofile',
            name='favourites',
            field=models.ManyToManyField(related_name='favourited_by', to='aristotle_mdr._concept', blank=True),
        ),
        migrations.AddField(
            model_name='possumprofile',
            name='savedActiveWorkgroup',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.Workgroup', null=True),
        ),
        migrations.AddField(
            model_name='possumprofile',
            name='user',
            field=models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='permissiblevalue',
            name='valueDomain',
            field=models.ForeignKey(related_name='permissiblevalue_set', to='aristotle_mdr.ValueDomain'),
        ),
        migrations.AddField(
            model_name='permissiblevalue',
            name='value_meaning',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ValueMeaning', null=True),
        ),

        migrations.AddField(
            model_name='discussionpost',
            name='relatedItems',
            field=models.ManyToManyField(related_name='relatedDiscussions', to='aristotle_mdr._concept', blank=True),
        ),
        migrations.AddField(
            model_name='discussionpost',
            name='workgroup',
            field=models.ForeignKey(related_name='discussions', to='aristotle_mdr.Workgroup'),
        ),
        migrations.AddField(
            model_name='discussioncomment',
            name='post',
            field=models.ForeignKey(related_name='comments', to='aristotle_mdr.DiscussionPost'),
        ),
        migrations.AddField(
            model_name='dataelementconcept',
            name='objectClass',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.ObjectClass', null=True),
        ),
        migrations.AddField(
            model_name='dataelementconcept',
            name='property',
            field=models.ForeignKey(blank=True, to='aristotle_mdr.Property', null=True),
        ),
        migrations.AddField(
            model_name='dataelementconcept',
            name='superseded_by',
            field=models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.DataElementConcept', null=True),
        ),
        migrations.AddField(
            model_name='dataelement',
            name='dataElementConcept',
            field=models.ForeignKey(verbose_name='Data Element Concept', blank=True, to='aristotle_mdr.DataElementConcept', null=True),
        ),
        migrations.AddField(
            model_name='dataelement',
            name='superseded_by',
            field=models.ForeignKey(related_name='supersedes', blank=True, to='aristotle_mdr.DataElement', null=True),
        ),
        migrations.AddField(
            model_name='dataelement',
            name='valueDomain',
            field=models.ForeignKey(verbose_name='Value Domain', blank=True, to='aristotle_mdr.ValueDomain', null=True),
        ),
        migrations.AddField(
            model_name='_concept',
            name='workgroup',
            field=models.ForeignKey(related_name='items', blank=True, to='aristotle_mdr.Workgroup', null=True),
        ),

        migrations.AddField(
            model_name='status',
            name='until_date',
            field=models.DateField(null=True, verbose_name='Date registration expires', blank=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='changeDetails',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='registrationDate',
            field=models.DateField(verbose_name='Date registration effective'),
        ),
        migrations.AlterUniqueTogether(
            name='status',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='status',
            name='inDictionary',
        ),
        migrations.RenameField(
            model_name='Measure',
            old_name='description',
            new_name='definition',
        ),
        migrations.RenameField(
            model_name='ConceptualDomain',
            old_name='value_description',
            new_name='description',
        ),
        migrations.AlterModelOptions(
            name='discussioncomment',
            options={'ordering': ['created']},
        ),
        migrations.AlterField(
            model_name='_concept',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='conceptualdomain',
            name='comments',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True),
        ),
        migrations.AlterField(
            model_name='conceptualdomain',
            name='references',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='comments',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True),
        ),
        migrations.AlterField(
            model_name='dataelement',
            name='references',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True),
        ),
        migrations.AlterField(
            model_name='dataelementconcept',
            name='comments',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True),
        ),
        migrations.AlterField(
            model_name='dataelementconcept',
            name='references',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True),
        ),
        migrations.AlterField(
            model_name='datatype',
            name='comments',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True),
        ),
        migrations.AlterField(
            model_name='datatype',
            name='references',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True),
        ),
        migrations.AlterField(
            model_name='measure',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='unitofmeasure',
            name='comments',
            field=ckeditor_uploader.fields.RichTextUploadingField(help_text='Descriptive comments about the metadata item.', blank=True),
        ),
        migrations.AlterField(
            model_name='unitofmeasure',
            name='references',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True),
        ),
        migrations.CreateModel(
            name='ReviewRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('message', models.TextField(help_text='An optional message accompanying a request', null=True, blank=True)),
                ('response', models.TextField(help_text='An optional message responding to a request', null=True, blank=True)),
                ('status', models.IntegerField(default=0, help_text='Status of a review', choices=[(0, 'Submitted'), (5, 'Cancelled'), (10, 'Accepted'), (15, 'Rejected')])),
                ('state', models.IntegerField(blank=True, help_text='The state at which a user wishes a metadata item to be endorsed', null=True, choices=[(0, 'Not Progressed'), (1, 'Incomplete'), (2, 'Candidate'), (3, 'Recorded'), (4, 'Qualified'), (5, 'Standard'), (6, 'Preferred Standard'), (7, 'Superseded'), (8, 'Retired')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='_concept',
            name='readyToReview',
        ),
        migrations.AddField(
            model_name='_concept',
            name='submitter',
            field=models.ForeignKey(related_name='created_items', blank=True, to=settings.AUTH_USER_MODEL, help_text='This is the person who first created an item. Users can always see items they made.', null=True),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='concepts',
            field=models.ManyToManyField(related_name='review_requests', to='aristotle_mdr._concept'),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='registration_authority',
            field=models.ForeignKey(help_text='The registration authority the requester wishes to endorse the metadata item', to='aristotle_mdr.RegistrationAuthority'),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='requester',
            field=models.ForeignKey(related_name='requested_reviews', to=settings.AUTH_USER_MODEL, help_text='The user requesting a review'),
        ),
        migrations.AddField(
            model_name='reviewrequest',
            name='reviewer',
            field=models.ForeignKey(related_name='reviewed_requests', to=settings.AUTH_USER_MODEL, help_text='The user performing a review', null=True),
        ),
    ]
