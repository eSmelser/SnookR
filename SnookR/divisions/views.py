# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

import itertools
from datetime import datetime

import functools
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django.views.generic.base import TemplateView, RedirectView
from functools import reduce
from rest_framework.renderers import JSONRenderer

from accounts.models import User
from api import serializers
from api.serializers import SessionEventSerializer
from divisions.forms import SubForm, CreateDivisionForm, CreateSessionForm, CreateRepeatedEventForm
from divisions.models import Division, Session, SessionEvent, DivRepRequest
from invites.models import SessionEventInvite
from substitutes.models import Sub
from teams.models import Team


class DivisionListView(TemplateView):
    template_name = 'divisions/divisions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Division.objects.all()
        return context


class DivisionView(TemplateView):
    template_name = 'divisions/division.html'

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
            user = User.objects.get(id=self.request.user.id)
            custom_user_serializer = serializers.CustomUserSerializer(user, context={'request': self.request})
            context['json']['current_user'] = JSONRenderer().render(custom_user_serializer.data)

            invites = SessionEventInvite.objects.filter(team__captain__user=self.request.user)
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
        session = self.kwargs.get('session')
        division = self.kwargs.get('division')
        return Session.objects.get(id=session, division__id=division)

    def user_is_registered(self, subs):
        return subs.filter(user=self.request.user).exists()

    def get_all_subs(self, session):
        return Sub.objects.filter(session_event=self.get_session_event(session))


class SessionView(LoginRequiredMixin, SessionViewMixin, TemplateView):
    template_name = 'divisions/session.html'


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


class SearchView(TemplateView):
    template_name = 'divisions/search.html'

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
            # Build a Q object that filters for available divisions that have last or first names that
            # starts with any of the search terms

            # 1.) Define all the Q objects
            first_name_queries = (Q(user__first_name__istartswith=term) for term in terms)
            last_name_queries = (Q(user__last_name__istartswith=term) for term in terms)

            # 2.) Reduce the Q objects into a single Q object by using the OR operator on each one together
            q_object = reduce(lambda q1, q2: q1 | q2, itertools.chain(last_name_queries, first_name_queries), Q())

            # 3.) Get the distinct IDs of each user to remove duplicates
            distinct_ids = Sub.objects.filter(q_object).values('user').distinct()

            # 4.) Filter on the distinct ids and set results
            context['results'] = User.objects.filter(id__in=distinct_ids)
        else:
            raise Http404('Invalid URL kwargs: ' + str(kwargs))

        return context


class SessionEventView(TemplateView):
    template_name = 'divisions/session_event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_event'] = get_object_or_404(SessionEvent, id=kwargs.get('pk'))
        subs = Sub.objects.filter(session_event=context['session_event'])
        if not self.request.user.is_authenticated():
            context['subs'] = subs
        else:
            context['subs'] = subs.exclude(user=self.request.user)
            context['teams'] = Team.objects.filter(captain__user=self.request.user)
            try:
                context['current_user_sub'] = subs.get(user=self.request.user)
            except Sub.DoesNotExist:
                context['current_user_sub'] = None

        return context


class SessionEventDetailView(FormView):
    template_name = 'divisions/session_event_detail.html'
    form_class = SubForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_event'] = self.get_session_event()
        subs = Sub.objects.filter(session_event=context['session_event'])
        if not self.request.user.is_authenticated():
            context['subs'] = subs
        else:
            context['subs'] = subs.exclude(user=self.request.user)
            context['teams'] = Team.objects.filter(captain__user=self.request.user)
            try:
                context['current_user_sub'] = subs.get(user=self.request.user)
            except Sub.DoesNotExist:
                context['current_user_sub'] = None

        context['session_events'] = self.get_session_events()
        return context

    @functools.lru_cache(maxsize=None)
    def get_session_event(self):
        return get_object_or_404(SessionEvent, id=self.kwargs.get('session_event'))

    def get_session_events(self):
        event = self.get_session_event()
        month = event.date.month
        session = event.session
        events = SessionEvent.objects.filter(session=session, date__month=month)
        serializer = SessionEventSerializer(events, many=True)
        return JSONRenderer().render(serializer.data)

    def form_valid(self, form):
        if self.is_register_post():
            Sub.objects.create(**form.cleaned_data)
        elif self.is_unregister_post():
            obj = Sub.objects.get(**form.cleaned_data)
            obj.delete()
        elif self.is_invite_post():
            obj = Sub.objects.get(**form.cleaned_data)
            sub_id = obj.id
            return redirect(reverse('invites:direct-sub-invite', kwargs={'sub_id': sub_id}))

        return super().form_valid(form)

    def form_invalid(self, form):
        # TODO: Determine a reasonable response to this form being invalid.  (Could it be invalid?  We generate it via templating)
        print('invalid', form.cleaned_data)
        print('data', self.request.POST)
        return super().form_invalid(form)

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret['data'] = {
            'user': self.request.POST.get('user', self.request.user.id),
            'session_event': self.get_session_event().id,
        }
        return ret

    def get_form(self, form_class=None):
        if self.request.method == 'GET':
            return None

        return self.get_form_class()(**self.get_form_kwargs())

    def is_register_post(self):
        return self.request.method == 'POST' and 'register' in self.request.POST

    def is_unregister_post(self):
        return self.request.method == 'POST' and 'unregister' in self.request.POST

    def is_invite_post(self):
        return self.request.method == 'POST' and 'invite' in self.request.POST


class DivRepPermissionMixin(PermissionRequiredMixin):
    permission_required = 'divisions.add_division'


class CreateDivisionView(DivRepPermissionMixin, FormView):
    template_name = 'divisions/div_rep_create_division.html'
    form_class = CreateDivisionForm
    success_url = reverse_lazy('divisions:div-rep-divisions-list')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        Division.objects.create(name=name, division_rep=self.request.user)
        return super().form_valid(form)


class DivRepDivisionsList(DivRepPermissionMixin, TemplateView):
    template_name = 'divisions/div_rep_divisions_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = self.request.user.divisions_set.all()
        return context

    def get(self, request, *args, **kwargs):
        if not self.request.user.divisions_set.all().count() > 0:
            return redirect(reverse('divisions:create-division'))

        return super().get(request, *args, **kwargs)


class DivRepCreateSessionView(DivRepPermissionMixin, FormView):
    template_name = 'divisions/div_rep_create_session.html'
    form_class = CreateSessionForm
    success_url = reverse_lazy('divisions:div-rep-divisions-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['division'] = self.get_division()
        return context

    def form_valid(self, form):
        division = self.get_division()
        Session.objects.create(division=division, **form.cleaned_data)
        return super().form_valid(form)

    def get_division(self):
        return get_object_or_404(Division, pk=self.kwargs.get('pk'))


class DivRepCreateSessionEventView(DivRepPermissionMixin, FormView):
    template_name = 'divisions/div_rep_create_session_event.html'
    form_class = CreateRepeatedEventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = self.get_session()
        return context

    def form_valid(self, form):
        session = self.get_session()
        print(form.cleaned_data)
        SessionEvent.objects.create_repeated(session=session, **form.cleaned_data)
        return super().form_valid(form)

    def get_session(self):
        return get_object_or_404(Session, pk=self.kwargs.get('pk'))

    def get_success_url(self):
        return reverse('divisions:div-rep-divisions-list')


class CreateDivRepRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'divisions/create_div_rep_request.html'

    def post(self, request, *args, **kwargs):
        DivRepRequest.objects.get_or_create(user=self.request.user)
        return redirect(reverse('divisions:div-rep-request-success'))


class DivRepRequestSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'divisions/div_rep_request_success.html'