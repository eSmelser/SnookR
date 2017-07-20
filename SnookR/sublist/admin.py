from django.contrib import admin
from sublist.models import Sublist


class SublistAdmin(admin.ModelAdmin):
    pass


admin.site.register(Sublist, SublistAdmin)
