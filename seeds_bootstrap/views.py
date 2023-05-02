from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import translation
from django.shortcuts import redirect

def index(request):
    return render(request,'index.html',{})

def selection(request):
    return render(request,'param_selection.html',{})

def aboutus(request):
    return render(request,'index.html',{})

def portfolio(request):
    return render(request,'portfolio.html')