import itertools

from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import ProcessFormView, FormView
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.db import IntegrityError

from invites.forms import TeamInviteForm
from invites.models import SessionEventInvite, TeamInvite
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
        print('subs', subs, 'ids', sub_ids)
        for sub in subs:
            try:
                SessionEventInvite.objects.create(team=team, sub=sub)
            except IntegrityError:
                # This captain already invited this player to this team on this day, nothing
                # needs to be done
                pass

        context = self.get_context_data(**kwargs)
        context['team'] = team
        context['subs'] = subs
        context['session'] = subs[0].session_event.session
        context['date'] = subs[0].session_event.date
        return self.render_to_response(context, **kwargs)


class InviteListView(FormView):
    template_name = 'invites/invites_list.html'
    success_url = reverse_lazy('invites:invites-list')

    def get_form(self, form_class=None):
        if self.request.method == 'GET':
            return None

        return super().get_form(form_class)

    def form_valid(self, form):
        model_class = self.get_model_class()
        obj = model_class.objects.get(**form.cleaned_data)
        obj.approve()
        return super().form_valid(form)

    def form_invalid(self, form):
        return HttpResponseBadRequest('Bad post data')

    def get_form_class(self):
        print(self.request.POST)
        if 'team' in self.request.POST:
            return TeamInviteForm
        if 'sub' in self.request.POST:
            #return SessionEventInviteForm
            pass

    def get_model_class(self):
        if 'team' in self.request.POST:
            return TeamInvite
        if 'sub' in self.request.POST:
            return SessionEventInvite

