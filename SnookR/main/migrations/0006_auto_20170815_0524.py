# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-15 05:24
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20170801_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='division',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=django.utils.timezone.now, editable=False, populate_from='name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=django.utils.timezone.now, editable=False, populate_from='name'),
            preserve_default=False,
        ),
    ]