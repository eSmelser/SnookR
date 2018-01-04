from django.views import View
from django.shortcuts import get_object_or_404, redirect
from invites.models import SessionEventInvite
from substitutes.models import SessionEvent, Sub


class SessionEventInviteView(View):
    def get(self, *args, **kwargs):
        sub = get_object_or_404(Sub, id=kwargs.get('sub'))
        session_event = get_object_or_404(SessionEvent, id=kwargs.get('session_event'))
        obj, created = SessionEventInvite.objects.get_or_create(invitee=sub, event=session_event)
        return redirect(self.request.META['HTTP_REFERER'])