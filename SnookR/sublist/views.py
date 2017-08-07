from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from sublist.models import Sublist
from main.models import Session, Player, Sub


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
        name = kwargs.get('session')
        context['session'] = Session.objects.get(
            name=name,
            sublist__slug=kwargs.get('sublist')
        )
        context['sublist'] = kwargs.get('sublist')

        return context



class SublistsView(TemplateView):
    '''A view for showing all sublists'''
    template_name = 'sublist/sublist_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sublists'] = Sublist.objects.all()
        return context
