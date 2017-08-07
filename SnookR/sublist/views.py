from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from sublist.models import Sublist
from main.models import Session, Player, Sub, Division, Location


class SublistView(TemplateView):
    """A view for presenting the sublist template"""
    template_name = 'sublist/sublist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('kwargs', kwargs)
        print('Sublist.objects.all()', Sublist.objects.all())
        context['sublist'] = get_object_or_404(Sublist, slug=kwargs.get('sublist'))
        return context


class RegisterSubSessionView(TemplateView):
    '''A view for registering players to a sublist'''
    template_name = 'sublist/register_sub.html'

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        sublist = get_object_or_404(Sublist, slug=kwargs.get('sublist'))
        session = Session.objects.filter(sublist=sublist)
        player = Player.objects.get(user=request.user)
        sub = Sub.objects.create(player=player)
        session.subs.add(sub)
        return ret


class SessionView(TemplateView):
    template_name = 'sublist/session.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = Session.objects.get(
            slug=kwargs.get('session'),
            division__slug=kwargs.get('division'),
        )
        context['session'] = session
        context['locations'] = Location.objects.filter(session=session)
        return context


class SublistsView(TemplateView):
    '''A view for showing all sublists'''
    template_name = 'sublist/sublist_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sublists'] = Sublist.objects.all()
        return context


class DivisionView(TemplateView):
    """A view for showing all sessions in a division"""
    template_name = 'sublist/division.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = Division.objects.get(slug=kwargs.get('division')).session_set.all()
        return context


class DivisionListView(TemplateView):
    """A view for showing all divisions"""
    template_name = 'sublist/division_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Division.objects.all()
        return context


class LocationView(TemplateView):
    """A view for showing a location"""
    template_name = 'sublist/location.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = Location.objects.get(
            slug=kwargs.get('location'),
            division__slug=kwargs.get('division'),
            session__slug=kwargs.get('session'),
        )
        return context

class LocationRegisterView(TemplateView):
    """A view for showing a location"""
    template_name = 'sublist/location_register.html'

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        location = self.get_location_instance(**kwargs)
        player, _ = Player.objects.get_or_create(user=self.request.user)
        sub, _ = Sub.objects.get_or_create(player=player)
        location.subs.add(sub)
        return ret


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = self.get_location_instance(**kwargs)
        return context

    def get_location_instance(self, **kwargs):
        return Location.objects.get(
            slug=kwargs.get('location'),
            division__slug=kwargs.get('division'),
            session__slug=kwargs.get('session'),
        )