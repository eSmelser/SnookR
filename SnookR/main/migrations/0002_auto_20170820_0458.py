# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-20 04:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='other_players',
            new_name='players',
        ),
    ]