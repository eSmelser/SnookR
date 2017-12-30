# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-30 22:22
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NonUserPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, default='', editable=False, populate_from='name')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, default='', editable=False, populate_from='name')),
                ('players', models.ManyToManyField(blank=True, to='accounts.CustomUser')),
                ('team_captain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_captain', to='accounts.CustomUser')),
            ],
            options={
                'permissions': (('create_team', 'Can create a team'),),
            },
        ),
        migrations.CreateModel(
            name='TeamInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('D', 'Declined')], default='P', max_length=1)),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.CustomUser')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Team')),
            ],
        ),
        migrations.AddField(
            model_name='nonuserplayer',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Team'),
        ),
    ]
