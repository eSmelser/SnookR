# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.contrib import admin
from substitutes.models import Sub
from divisions.models import Division, Session

admin.site.register(Sub)
admin.site.register(Division)
admin.site.register(Session)