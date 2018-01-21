import itertools
from django.views.generic import TemplateView
from rest_framework.renderers import JSONRenderer

from accounts.models import User
from api import serializers
from substitutes.models import Sub
from divisions.models import Session
from teams.models import Team


class HomeView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            try:
                # Gets all foreign keys in a single query
                # Note: ordering is required for itertools.groupby to work
                subs = Sub.objects.select_related('session_event__session__division') \
                    .filter(user=self.request.user) \
                    .order_by('session_event__session__division', 'session_event__session',
                              'session_event__date', 'session_event__start_time')

                data = []
                # Group by division
                for division, subs_by_division in itertools.groupby(subs,
                                                                    lambda obj: obj.session_event.session.division):
                    division_data = {'instance': division, 'sessions': []}

                    # Further group by session
                    for session, subs_by_session in itertools.groupby(subs_by_division,
                                                                      lambda obj: obj.session_event.session):
                        session_data = {
                            'instance': session,
                            'session_events': [sub.session_event for sub in subs_by_session]
                        }
                        division_data['sessions'].append(session_data)

                    data.append(division_data)

                context['divisions'] = data

                serializer = serializers.SessionEventSerializer((sub.session_event for sub in subs), many=True)
                context['session_events_json'] = JSONRenderer().render(serializer.data)

            except User.DoesNotExist:
                pass
        else:
            context['sub_count'] = len(set(sub.user for sub in Sub.objects.all()))
            context['sessions'] = Session.objects.all()
            context['sessions_count'] = len(Session.objects.all())

        context['teams'] = Team.get_all_related(self.request.user)
        return context