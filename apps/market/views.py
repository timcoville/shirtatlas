from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from models import *


def index(request):
    query = request.GET.get('name')
    print(query)
    return render(request, "market/index.html")

def test(request):
    return render(request, "market/designs.html")

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

def editprofile(request):
    if not 'user_id' in request.session:
        return redirect('/')
    if request.method != 'POST':
        context = {"user": User.objects.get(id = request.session['user_id'])}
        return render(request, "market/edit.html", context)
    result = User.objects.update_profile(request.POST)
    if "errors" in result:
        for error in result['errors']:
            messages.error(request, error)
        return redirect('/editprofile')
    messages.success(request, "Profile Updateded Successfully")
    return redirect('/editprofile')

def editpassword(request):
    if not 'user_id' in request.session:
        return redirect('')
    if request.method != 'POST':
        return render(request, "market/password.html")
    result = User.objects.update_password(request.POST)
    if 'errors' in result:
        for error in result['errors']:
            messages.error(request, error)
        return redirect('/editpassword')
    messages.success(request, "Password Updated Successfully")
    return redirect('/editprofile')

def newdesign(request):
    if not 'user_id' in request.session and not 'designer' in request.session:
        return redirect('')
    if request.method != 'POST':
        return render(request, "market/newdesign.html")
    print(request.POST)
    result = Design.objects.upload_design(request.POST, request.FILES)
    if 'errors' in result:
        for error in result['errors']:
            messages.error(request, error)
        return redirect('/newdesign')
    print(result)
    design = result['design']
    print(design)
    route = "/"
    route += str(design.id)
    return redirect(route)

def design(request, id):
    context = {
        'design': Design.objects.get(id=id)
        }
    return render(request, "market/design.html", context)

def portfolio(request, id):
    if not 'user_id' in request.session and not 'designer' in request.session:
        return redirect('/')
    user = User.objects.get(id = id)
    
    designs = Design.objects.filter(designer = user).order_by('-created_at')
    context = {
        'user': user,
        'designs': designs
    }
    return render(request, "market/designs.html", context)

def edit(request, user_id, design_id):
    if not 'user_id' in request.session and not 'designer' in request.session:
        return redirect('/')
    if int(user_id) != request.session['user_id']:
        return redirect('/')
    return redirect('/')

def delete(request, user_id, design_id):
    if not 'user_id' in request.session and not 'designer' in request.session:
        return redirect('/')
    if int(user_id) != request.session['user_id']:
        return redirect('/')
    Design.objects.get(id=design_id).delete()
    return redirect('/portfolio/'+user_id)

def pause(request, user_id, design_id):
    print('hitting route')
    if not 'user_id' in request.session and not 'designer' in request.session:
        return redirect('/')
    if int(user_id) != request.session['user_id']:
        return redirect('/')
    design = Design.objects.get(id=design_id)
    if (design.paused):
        design.paused = False
        design.save()
        return redirect('/portfolio/'+user_id)
    design.paused = True
    design.save()    
    return redirect('/portfolio/'+user_id)

def logout(request):
    request.session.clear()
    return redirect('/')
    


"""
    Review with Patrick:

     print(id)
    print('-------')
    print(request.session['user_id'])
    test = int(request.session['user_id'])
    print(id == test)
    print(1 == 1)
    if id == request.session['user_id']:
        return redirect('/')
 """