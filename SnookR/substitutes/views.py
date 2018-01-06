# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

import itertools
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateView, RedirectView
from functools import reduce
from rest_framework.renderers import JSONRenderer

from accounts.models import CustomUser
from api import serializers
from substitutes.models import Division, Session, SessionEvent, Sub
from invites.models import SessionEventInvite
from teams.models import Team

class DivisionListView(TemplateView):
    template_name = 'substitutes/divisions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Division.objects.all()
        return context


class DivisionView(TemplateView):
    template_name = 'substitutes/division.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('division')
        division = get_object_or_404(Division, slug=slug)

        session_events = SessionEvent.objects.filter(session__division=division)
        serializer = serializers.SessionEventSerializer(session_events, many=True)
        context['division'] = division
        context['session_events_json'] = JSONRenderer().render(serializer.data)
        return context


class SessionViewMixin(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session = self.get_session_instance()
        session_event = self.get_session_event(session)
        session_events = self.get_session_events(session)
        subs = self.get_all_subs(session)
        user_registered = self.user_is_registered(subs)

        context['session'] = session
        context['session_event'] = session_event
        context['user_registered'] = user_registered

        # Separate current user from the normal list of subs so they can be given a special display
        if user_registered:
            context['subs'] = subs.exclude(user=self.request.user)
            context['current_user_sub'] = subs.get(user=self.request.user)
        else:
            context['subs'] = subs
            context['current_user_sub'] = None

        context = self.jsonify_context(session_event, session_events, subs, context)
        return context

    def jsonify_context(self, session_event, session_events, subs, context):
        subs_serializer = serializers.SubSerializer(subs, many=True, context={'request': self.request})
        event_serializer = serializers.SessionEventSerializer(session_event)
        events_serializer = serializers.SessionEventSerializer(session_events, many=True)

        context['json'] = dict()
        if self.request.user.is_authenticated():
            user = CustomUser.objects.get(id=self.request.user.id)
            custom_user_serializer = serializers.CustomUserSerializer(user, context={'request': self.request})
            context['json']['current_user'] = JSONRenderer().render(custom_user_serializer.data)

            invites = SessionEventInvite.objects.filter(captain=self.request.user)
            invites_serializer = serializers.SessionEventInviteSerializer(invites, many=True)
            context['json']['current_user_previous_invites'] = JSONRenderer().render(invites_serializer.data)

        context['json']['session_event'] = JSONRenderer().render(event_serializer.data)
        context['json']['session_events'] = JSONRenderer().render(events_serializer.data)
        context['json']['subs'] = JSONRenderer().render(subs_serializer.data)
        return context

    def get_session_event(self, session):
        id = self.request.GET.get('sessionEventId', False)
        if not id:
            return self.get_session_events(session).filter(date__month=datetime.now().month).first()
        else:
            return get_object_or_404(SessionEvent, id=id)

    def get_session_events(self, session):
        return SessionEvent.objects.filter(session=session).order_by('date')

    def get_session_instance(self):
        session_slug = self.kwargs.get('session')
        division_slug = self.kwargs.get('division')
        return Session.objects.get(slug=session_slug, division__slug=division_slug)

    def user_is_registered(self, subs):
        return subs.filter(user=self.request.user).exists()

    def get_all_subs(self, session):
        return Sub.objects.filter(session_event=self.get_session_event(session))


class SessionView(LoginRequiredMixin, SessionViewMixin, TemplateView):
    template_name = 'substitutes/session.html'


class SessionEventRegisterView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        Sub.objects.create(session_event=SessionEvent.objects.get(id=id), user=self.request.user)
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        # Redirect back to where you came from!
        return self.request.environ['HTTP_REFERER']


class SessionEventUnregisterView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        id = kwargs.get('pk')
        qs = Sub.objects.filter(session_event=SessionEvent.objects.get(id=id), user=self.request.user)
        if qs.exists():
            qs.delete()

        # Redirect back to where you came from!
        return self.request.environ['HTTP_REFERER']


class SessionRegisterSuccessView(RedirectView, SessionViewMixin):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('home')


class SessionUnregisterView(RedirectView, SessionViewMixin):
    def get_redirect_url(self, *args, **kwargs):
        date = datetime.strptime(kwargs.get('date'), Session.date_format)
        session = get_object_or_404(Session, slug=kwargs.get('session'), division__slug=kwargs.get('division'))
        session.remove_user_as_sub(self.request.user, date=date)
        return reverse('home')


class InviteListView(TemplateView):
    template_name = 'substitutes/invites.html'


class SearchView(TemplateView):
    template_name = 'substitutes/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms = self.request.GET['query'].split()
        search_type = kwargs.get('search_type', None)

        if search_type == 'session':
            # Build a Q object that check if the name column contains any of the terms in search
            q_object = reduce(lambda q1, q2: q1 | q2, (Q(name__contains=term) for term in terms), Q())

            # Filter sessions on the previously built Q object
            context['results'] = Session.objects.filter(q_object)
        elif search_type == 'substitute':
            # Build a Q object that filters for available substitutes that have last or first names that
            # starts with any of the search terms

            # 1.) Define all the Q objects
            first_name_queries = (Q(user__first_name__istartswith=term) for term in terms)
            last_name_queries = (Q(user__last_name__istartswith=term) for term in terms)

            # 2.) Reduce the Q objects into a single Q object by using the OR operator on each one together
            q_object = reduce(lambda q1, q2: q1 | q2, itertools.chain(last_name_queries, first_name_queries), Q())

            # 3.) Get the distinct IDs of each user to remove duplicates
            distinct_ids = Sub.objects.filter(q_object).values('user').distinct()

            # 4.) Filter on the distinct ids and set results
            context['results'] = CustomUser.objects.filter(id__in=distinct_ids)
        else:
            raise Http404('Invalid URL kwargs: ' + str(kwargs))

        return context


class SessionEventView(TemplateView):
    template_name = 'substitutes/session_event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_event'] = get_object_or_404(SessionEvent, id=kwargs.get('pk'))
        subs = Sub.objects.filter(session_event=context['session_event'])
        if not self.request.user.is_authenticated():
            context['subs'] = subs
        else:
            context['subs'] = subs.exclude(user=self.request.user)
            context['teams'] = Team.objects.filter(team_captain=self.request.user)
            try:
                context['current_user_sub'] = subs.get(user=self.request.user)
            except Sub.DoesNotExist:
                context['current_user_sub'] = None

        return context
