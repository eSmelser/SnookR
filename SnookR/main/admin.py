from django.contrib import admin
from .models import Player
from .models import Sub
from .models import Team
from .models import Division
from .models import Session


admin.site.register(Player)
admin.site.register(Sub)
admin.site.register(Team)
admin.site.register(Division)
admin.site.register(Session)


