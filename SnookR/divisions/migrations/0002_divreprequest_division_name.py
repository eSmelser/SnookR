# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-23 02:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divisions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='divreprequest',
            name='division_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]