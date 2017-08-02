from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from sublist.models import Sublist


class SublistView(TemplateView):
    """A view for presenting the sublist template"""
    template_name = 'sublist/sublist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('kwargs', kwargs)
        print('Sublist.objects.all()', Sublist.objects.all())
        context['sublist'] = get_object_or_404(Sublist, slug=kwargs.get('sublist'))
        return context

class RegisterSubView(TemplateView):
    '''A view for registering players to a sublist'''
    template_name='sublist/register_sub.html'
