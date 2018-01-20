# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-20 01:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('divisions', '0005_auto_20180120_0159'),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Captain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='divisions.Division')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.CustomUser')),
            ],
        ),
        migrations.RemoveField(
            model_name='team',
            name='team_captain',
        ),
        migrations.AddField(
            model_name='team',
            name='captain',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='managed_teams', to='teams.Captain'),
            preserve_default=False,
        ),
    ]