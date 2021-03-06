# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-30 01:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comet', '0002_squashed_0003_auto_20170714_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='framework',
            name='indicators',
            field=models.ManyToManyField(blank=True, related_name='frameworks', to='comet.Indicator'),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='outcome_areas',
            field=models.ManyToManyField(blank=True, related_name='indicators', to='comet.OutcomeArea'),
        ),
    ]
