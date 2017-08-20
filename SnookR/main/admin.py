# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.contrib import admin
from .models import UserProfile
from .models import Sub
from .models import Team
from .models import Division
from .models import Session


admin.site.register(UserProfile)
admin.site.register(Sub)
admin.site.register(Team)
admin.site.register(Division)
admin.site.register(Session)


