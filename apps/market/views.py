from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from models import *

import os
import stripe

stripe.api_key = os.environ.get('STRIPE_PRIVATE_KEY')





states = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE",  "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
cats = ["Tattoo", "Bikers", "Characters", "Heraldry",  "Holiday", "Photoshop", "Religious", "Skulls", "Sports", "Typography", "Urban", "Patterns", "Funny", "Artistic", "Comics", "Retro", "Sci-Fi", "Gym", "Abstract", "Anime", "Dogs", "Birds", "Cats", "Cool", "Fantasy", "Gaming", "Horror", "Monsters", "Music", "Zombies", "Cars", "Yoga", "Miscellaneous", "Nature", "Geek", "Camping", "Love", "Pregnancy", "Party", "Animals"]

def index(request):
    context = {
        'new_designs': Design.objects.filter(paused = False).exclude(on_sale = True).order_by('-id')[:5],
        'sale_designs': Design.objects.filter(on_sale = True).order_by('-id')[:5],
    }

    designs = Design.objects.raw('SELECT * FROM market_design JOIN market_user ON market_design.id = market_user.id')
    for design in designs:
        print(design)
    print(designs)


    return render(request, "market/index.html", context)

def index2(request):
    query = request.GET.get('name')
    print(query)
    return render(request, "market/index.html")


def cart(request):
    if not 'cart' in request.session:
        request.session['cart'] = []
    results = []
    cart_price = 0
    for id in request.session['cart']:
        design = Design.objects.get(id=id)
        if design.paused:
            messages.error(request, design.name + " has been removed from marketplace, apologies")
        else:
            if design.on_sale:
                discount = design.price * Decimal(.9)
                design.final_price = Decimal(format(float(discount), '.2f'))
                cart_price += design.final_price
                design.save()
                print(cart_price)
            else:
                cart_price += design.price
            results.append(design)
        
    if len(results) == 0:
        cart_empty = True
    else:
        cart_empty = False
    context = {
        'designs': results,
        'cart_total': cart_price,
        'cart_empty': cart_empty
    }
    return render(request, "market/cart.html", context)

def add_to_cart(request, design_id):
    if 'backURL' in request.POST:
        messages.info(request, request.POST['backURL'])
    try:
        design = Design.objects.get(id=design_id)
    except:
        return redirect('/')
    if not 'cart' in request.session:
        request.session['cart'] = []
    cart = request.session['cart']
    url = request.POST['refURL']
    print(url[len(url)-1])
    if url[len(url)-1] == '?':
        url = url.replace('?',"")
    
    if design.id in cart:
        messages.error(request, "Design already added to cart!")
        return redirect(url)
    else:
        cart.append(design.id)
        request.session['cart'] = cart
        return redirect(url)

def remove_from_cart(request, design_id):
    if 'backURL' in request.POST:
        messages.info(request, request.POST['backURL'])

    url = request.POST['refURL']
    if url[len(url)-1] == '?':
        url = url.replace('?',"")
    cart = request.session['cart']
    if not int(design_id) in cart:
        print('working')
        url = request.POST['refURL']
        return redirect(url)

    del cart[cart.index(int(design_id))]
    request.session['cart'] = cart
    
    
    return redirect(url)
    
def checkout(request):
    return render(request, "market/checkout.html")


def designs(request):
    category = request.GET.get('cat')
    
    
    if category != None and ' ' in category:
        category = category.split(' ')
        

    if category != None:
        if type(category) == list:
            results = Design.objects.filter(categories__overlap = category)
        else:
            results = Design.objects.filter(categories__contains = [category])
    else:
        results = Design.objects.all()
    print(results)
    page = request.GET.get('page', 1)
    
    paginator = Paginator(results, 4)
    
    try:
        designs = paginator.page(page)
    except PageNotAnInteger:
        designs = paginator.page(1)
    except EmptyPage:
        designs = paginator.page(paginator.num_pages)

    page_string = ""
    if type(category) == list:
        for index, catString in enumerate(category):
            print(index)
            print(len(category))
            if len(category)-1 == index:
                page_string += catString
            else:    
                page_string += catString + "+"
    else:
        page_string = category
    print(page_string)

    context = {
        'cats': cats,
        'current_cat': category,
        'designs': designs,
        'string_url': page_string
    }
    return render(request, "market/designs.html", context)

def register(request):
    if request.method != 'POST':
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
    if not 'user_id' in request.session or not 'designer' in request.session:
        return redirect('/')
    if request.method != 'POST':
        return render(request, "market/newdesign.html", {'cats': cats})
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
    design = Design.objects.get(id=id)

    context = {
        'design': design,
        'cats': cats
        }
    return render(request, "market/design.html", context)

def portfolio(request, id):
    if not 'user_id' in request.session or not 'designer' in request.session:
        return redirect('/')

    page = request.GET.get('page', 1)
    results = Design.objects.filter(designer = User.objects.get(id = id)).order_by('-created_at')
    paginator = Paginator(results, 4)
    
    try:
        designs = paginator.page(page)
    except PageNotAnInteger:
        designs = paginator.page(1)
    except EmptyPage:
        designs = paginator.page(paginator.num_pages)
    
    context = {
        'designs': designs
    }
    return render(request, "market/portfolio.html", context)

def editdesign(request, user_id, design_id):
    if not 'user_id' in request.session or not 'designer' in request.session:
        return redirect('/')
    if int(user_id) != request.session['user_id']:
        return redirect('/')
    if request.method != 'POST':
        context = {
            'design' : Design.objects.get(id=design_id),
            'cats': cats
        }
        return render(request, "market/editdesign.html", context)
    result = Design.objects.edit_design(request.POST, request.FILES)
    if 'errors' in result:
        for error in result['errors']:
            messages.error(request, error)
        return redirect('/portfolio/'+user_id+'/edit/'+design_id)        
    
    
    return redirect('/portfolio/'+user_id)

def delete(request, user_id, design_id):
    if not 'user_id' in request.session or not 'designer' in request.session:
        return redirect('/')
    if int(user_id) != request.session['user_id']:
        return redirect('/')
    Design.objects.get(id=design_id).delete()
    return redirect('/portfolio/'+user_id)

def pause(request, user_id, design_id):
    if not 'user_id' in request.session or not 'designer' in request.session:
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

def sale(request, user_id, design_id):
    if not 'user_id' in request.session or not 'designer' in request.session:
        return redirect('/')
    if int(user_id) != request.session['user_id']:
        return redirect('/')
    design = Design.objects.get(id=design_id)
    if (design.on_sale):
        design.on_sale = False
        design.final_price = design.price
        design.save()
        return redirect('/portfolio/'+user_id)
    design.on_sale = True
    design.sale_price
    design.save()    
    return redirect('/portfolio/'+user_id)

def logout(request):
    request.session.clear()
    return redirect('/')
    


