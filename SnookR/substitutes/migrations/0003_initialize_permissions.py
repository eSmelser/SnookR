from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from accounts.models import CustomUser


def create_groups(apps, schema_editor):
    group, created = Group.objects.get_or_create(name='Division Representatives')
    if created:
        content_type = ContentType.objects.get_for_model(CustomUser)
        perm = Permission.objects.get(content_type=content_type, codename='can_permit_add_team')
        group.permissions.add(perm)

    group, created = Group.objects.get_or_create(name='Team Captains')
    if created:
        perm = Permission.objects.get(codename='add_team')
        group.permissions.add(perm)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_auto_20180113_1952'),
        ('substitutes', '0001_initial'),
        ('accounts', '0006_auto_20180116_1636'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
