# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-08 05:44
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0022_switch_to_concept_relations'),
        ('aristotle_dse', '0014_auto_20161023_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributiondataelementpath',
            name='specialisation_classes',
            field=aristotle_mdr.fields.ConceptManyToManyField(to='aristotle_mdr.ObjectClass'),
        ),
        migrations.AddField(
            model_name='dssdeinclusion',
            name='specialisation_classes',
            field=aristotle_mdr.fields.ConceptManyToManyField(to='aristotle_mdr.ObjectClass'),
        ),
        migrations.AlterField(
            model_name='datasetspecification',
            name='clusters',
            field=aristotle_mdr.fields.ConceptManyToManyField(blank=True, null=True, through='aristotle_dse.DSSClusterInclusion', to='aristotle_dse.DataSetSpecification'),
        ),
        migrations.AlterField(
            model_name='datasetspecification',
            name='data_elements',
            field=aristotle_mdr.fields.ConceptManyToManyField(blank=True, null=True, through='aristotle_dse.DSSDEInclusion', to='aristotle_mdr.DataElement'),
        ),
        migrations.AlterField(
            model_name='datasetspecification',
            name='statistical_unit',
            field=aristotle_mdr.fields.ConceptForeignKey(blank=True, help_text='Indiciates if the ordering for a dataset is must match exactly the order laid out in the specification.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='statistical_unit_of', to='aristotle_mdr._concept'),
        ),
        migrations.AlterField(
            model_name='distribution',
            name='specification',
            field=aristotle_mdr.fields.ConceptForeignKey(blank=True, help_text='The dataset specification to which this data source conforms', null=True, on_delete=django.db.models.deletion.CASCADE, to='aristotle_dse.DataSetSpecification'),
        ),
        migrations.AlterField(
            model_name='distributiondataelementpath',
            name='data_element',
            field=aristotle_mdr.fields.ConceptForeignKey(blank=True, help_text='An entity responsible for making the dataset available.', null=True, on_delete=django.db.models.deletion.CASCADE, to='aristotle_mdr.DataElement'),
        ),
        migrations.AlterField(
            model_name='dssclusterinclusion',
            name='child',
            field=aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_dss', to='aristotle_dse.DataSetSpecification'),
        ),
        migrations.AlterField(
            model_name='dssclusterinclusion',
            name='dss',
            field=aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aristotle_dse.DataSetSpecification'),
        ),
        migrations.AlterField(
            model_name='dssdeinclusion',
            name='data_element',
            field=aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dssInclusions', to='aristotle_mdr.DataElement'),
        ),
        migrations.AlterField(
            model_name='dssdeinclusion',
            name='dss',
            field=aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aristotle_dse.DataSetSpecification'),
        ),
    ]
