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
    result = User.objects.create_user(request.POST)
    if 'errors' in result:
        for error in result['errors']:
            messages.error(request, error)
        return redirect ('/register')
    if 'user' in result:
        request.session['user_id'] = result['user'].id
        if result['user'].designer == True:
            print("works")
            request.session['designer'] = "true"
        return redirect('/')
    
def login(request):
    if request.method != 'POST':
        return render(request, "market/login.html")
    result = User.objects.login_user(request.POST)
    if 'errors' in result:
        for error in result['errors']:
            messages.error(request, error)
        return redirect ('/login')
    if 'user' in result:
        request.session['user_id'] = result['user'].id
        if result['user'].designer == True:
            print("works")
            request.session['designer'] = True
        return redirect('/')

def editprofile(request, id):
    if not 'user_id' in request.session:
        return redirect('/')
    if request.method != 'POST':
        context = {"user": User.objects.get(id = id)}
        return render(request, "market/edit.html", context)
    

def logout(request):
    request.session.clear()
    return redirect('/')
    
    