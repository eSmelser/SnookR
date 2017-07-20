from django.db import models
from django.template.defaultfilters import slugify

class Sublist(models.Model):
    name = models.CharField(blank=False, max_length=100)
    slug = models.SlugField(blank=False, max_length=120)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sublist, self).save(*args, **kwargs)
