import itertools
from django.views import View
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.edit import ProcessFormView
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.db import IntegrityError
from invites.models import SessionEventInvite
from substitutes.models import SessionEvent, Sub, Session
from api.serializers import SessionEventSerializer, SubSerializer
from rest_framework.renderers import JSONRenderer
from teams.models import Team


class SessionEventStartView(TemplateView):
    template_name = 'invites/session_event_start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = Team.objects.filter(team_captain=self.request.user)
        return context


class SessionSelectView(TemplateView):
    template_name = 'invites/session_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = []
        qs = Session.objects.all().order_by('division__name')
        groups = itertools.groupby(qs, lambda obj: obj.division.name)
        for group, session in groups:
            # Iterators tended to lose values at random inside the template, so we instantiate
            # it as a list here.
            session = list(session)
            context['groups'].append({'division': group, 'sessions': session})

        return context

class SessionEventSelectView(TemplateView):
    template_name = 'invites/session_event_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = SessionEvent.objects.filter(session__id=kwargs.get('session_id'))
        serializer = SessionEventSerializer(qs, many=True)

        # Add subs to the data copy
        copy = list(serializer.data)
        for i, data in enumerate(serializer.data):
            qs = Sub.objects.filter(session_event__id=data['id'])
            serializer = SubSerializer(qs, many=True)
            copy[i]['subs'] = serializer.data

        context['session_events'] = JSONRenderer().render(copy)
        return context

class SessionEventInviteConfirmView(TemplateView):
    template_name = 'invites/session_event_invite_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ids = self.request.GET.getlist('sub')
        team_id = self.request.GET.get('teamId')
        context['subs'] = Sub.objects.filter(id__in=ids)

        # We all session events in this view will be on the same date and same session.
        # So we just grab the first one and use that as our reference data and session
        first = context['subs'].first()
        context['date'] = first.session_event.date
        context['session'] = first.session_event.session
        context['team'] = get_object_or_404(Team, id=team_id)
        return context

class SessionEventInviteCreateView(TemplateResponseMixin, ContextMixin, ProcessFormView):
    template_name = 'invites/session_event_invite_create.html'

    def post(self, *arg, **kwargs):
        team_id = self.request.POST.get('team-id')
        sub_ids = self.request.POST.getlist('sub')
        team = Team.objects.get(id=team_id)
        subs = Sub.objects.filter(id__in=sub_ids)
        for sub in subs:
            try:
                SessionEventInvite.objects.create(team=team, sub=sub)
            except IntegrityError:
                # This captain already invited this player to this team on this day, nothing
                # needs to be done
                pass

        return self.render_to_response(self.get_context_data(team=team, subs=subs, **kwargs))
