from django.db import models

class Sublist(models.Model):
    name = models.CharField(blank=False, max_length=100)
