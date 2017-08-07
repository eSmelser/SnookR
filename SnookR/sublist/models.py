from django.db import models
from autoslug import AutoSlugField
from django.urls import reverse


class Sublist(models.Model):
    location = models.ForeignKey('main.Location')

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('sublist', kwargs={'sublist': str(self.slug)})