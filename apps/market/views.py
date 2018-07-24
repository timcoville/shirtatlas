from django.shortcuts import render, HttpResponse
from models import *

def index(request):

    return render(request, "market/index.html")