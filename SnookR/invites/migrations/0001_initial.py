# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-19 02:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('substitutes', '0001_initial'),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionEventInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('D', 'Declined')], default='P', max_length=1)),
                ('sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='substitutes.Sub')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Team')),
            ],
        ),
        migrations.CreateModel(
            name='TeamInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('D', 'Declined')], default='P', max_length=1)),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.CustomUser')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='sessioneventinvite',
            unique_together=set([('sub', 'team')]),
        ),
    ]
