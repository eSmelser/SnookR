# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.contrib import admin
from sublist.models import Sublist


class SublistAdmin(admin.ModelAdmin):
    pass


admin.site.register(Sublist, SublistAdmin)
