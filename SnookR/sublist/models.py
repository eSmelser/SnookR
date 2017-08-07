from django.db import models
from autoslug import AutoSlugField


class Sublist(models.Model):
    name = models.CharField(blank=False, max_length=100)
    slug = AutoSlugField(populate_from='name')
    session = models.OneToOneField('main.Session')

    def __str__(self):
        return str(self.name) + ': ' + str(self.session)
