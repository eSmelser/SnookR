from django.db import models
from autoslug import AutoSlugField
from django.urls import reverse


class Sublist(models.Model):
    name = models.CharField(blank=False, max_length=100)
    slug = AutoSlugField(populate_from='name')
    session = models.OneToOneField('main.Session')

    def __str__(self):
        return str(self.name) + ': ' + str(self.session)

    def get_absolute_url(self):
        return reverse('sublist', kwargs={'sublist': str(self.slug)})