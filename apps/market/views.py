from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from models import *

def index(request):
    
    return render(request, "market/index.html")

def register(request):
    if request.method != 'POST':
        states = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE",  "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
        context = {'states': states}
        return render(request, "market/register.html", context)
    print(request.POST)
    print(request.POST)
    return redirect('/register')
    
def login(request):
    if request.method != 'POST':
        return render(request, "market/login.html")

    print (request.POST)
    return redirect('/login')
    
    