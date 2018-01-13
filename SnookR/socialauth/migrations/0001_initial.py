# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-13 18:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_userprofile_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookAuth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook_id', models.CharField(max_length=32)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.CustomUser')),
            ],
        ),
    ]
