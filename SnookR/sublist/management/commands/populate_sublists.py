from django.core.management.base import BaseCommand, CommandError
from sublist.models import Sublist

class Command(BaseCommand):
    help = 'Adds sublists to the db'
    names = [
        'Fortune Star',
        'Local 66',
        'McAnulty and Barrys',
        'Outer Eastside',
        'Pub 181',
        'River Roadhouse',
        'Watertrough',
        'Wichita'
    ]

    def handle(self, *args, **options):
        Sublist.objects.all().delete()
        for name in self.names:
            Sublist.objects.create(name=name)
        self.stdout.write(self.style.SUCCESS('Successfully filled sublist database '))
