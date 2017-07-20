from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from sublist.models import Sublist


class SublistView(TemplateView):
    """A view for presenting the sublist template"""
    template_name = 'sublist/sublist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sublist'] = get_object_or_404(Sublist, name=kwargs.get('name'))
        return context


def wichita(request):
	return HttpResponse("Wichita's sublist")

def river_roadhouse(request):
	return HttpResponse("River Roadhouse's sublist")

def mcanulty_and_barrys(request):
	return HttpResponse("McAnulty and Barry's sublist")

def local66(request):
	return HttpResponse("Local 66 sublist")

def watertrough(request):
	return HttpResponse("Watertrough sublist")

def fortune_star(request):
	return HttpResponse("Fortune Star sublist")

def pub181(request):
	return HttpResponse("Pub 181 sublist")

def outer_eastside(request):
	return HttpResponse("Outer Eastside sublist")
