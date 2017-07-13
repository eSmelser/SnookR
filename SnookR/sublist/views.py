from django.shortcuts import render
from django.http import HttpResponse

 
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

