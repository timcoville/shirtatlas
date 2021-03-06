from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from models import *

import os
import stripe

stripe.api_key = os.environ.get('STRIPE_PRIVATE_KEY')
public_key = os.environ.get('STRIPE_PUBLIC_KEY')


states = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE",  "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
cats = ["Tattoo", "Bikers", "Characters", "Heraldry",  "Holiday", "Photoshop", "Religious", "Skulls", "Sports", "Typography", "Urban", "Patterns", "Funny", "Artistic", "Comics", "Retro", "Sci-Fi", "Gym", "Abstract", "Anime", "Dogs", "Birds", "Cats", "Cool", "Fantasy", "Gaming", "Horror", "Monsters", "Music", "Zombies", "Cars", "Yoga", "Miscellaneous", "Nature", "Geek", "Camping", "Love", "Pregnancy", "Party", "Animals"]

def index(request):
    context = {
        'new_designs': Design.objects.filter(paused = False).exclude(on_sale = True).order_by('-id')[:5],
        'sale_designs': Design.objects.filter(on_sale = True).exclude(paused=True).order_by('-id')[:5],
    }
    return render(request, "market/index.html", context)

def cart(request):
    if not 'user_id' in request.session:
        messages.error(request, "Please login or register to checkout")        
    if not 'cart' in request.session:
        request.session['cart'] = []
    results = []
    prices = []
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
                prices.append(design.final_price)
            else:
                cart_price += design.price
                prices.append(design.price)
            results.append(design)
    if request.method != 'POST':
        if len(results) == 0:
            cart_empty = True
        else:
            cart_empty = False
        charge_price = int(cart_price * 100)
        context = {
            'designs': results,
            'cart_total': cart_price,
            'cart_empty': cart_empty,
            'charge_price': charge_price,
            'public_key': public_key
        }
        return render(request, "market/cart.html", context)
    else:
        try: 
            charge = stripe.Charge.create(
                amount=int(cart_price * 100),
                currency="usd",
                source=request.POST['stripeToken'],
                description="Design license(s) purchases with Shirt Atlas"
            )
        except stripe.error.CardError as ce:
            messages.error(request, "Failure to process your credit card, please try again")
            return redirect('/cart')
        
        new_order = Order.objects.create(token_id=request.POST['stripeToken'], buyer=User.objects.get(id = request.session['user_id']), order_cost = cart_price, charge_id = charge.id)
        for design in results:
            if design.on_sale:
                OrderDetails.objects.create(charged_price = design.final_price, design = design, order = new_order)
            else:
                OrderDetails.objects.create(charged_price = design.price, design = design, order = new_order)
            design.licenses -= 1
            design.sales += 1
            design.save()
        request.session['cart'] = []
        return redirect('/success')

def success(request):
    return render(request, 'market/success.html')

def view_orders(request):
    if not 'user_id' in request.session:
        return redirect('/')
    user = User.objects.get(id = request.session['user_id'])
    results = Order.objects.filter(buyer_id = user.id)
    context = {
        'orders': results,
        'user': user
    }
    return render(request, 'market/vieworders.html', context)

def order_details(request, order_id, user_id):
    if not 'user_id' in request.session:
        return redirect('/')
    if request.session['user_id'] != int(user_id):
        return redirect('/vieworders')
    orders = OrderDetails.objects.filter(order_id = order_id).prefetch_related()
    context = {
        'orders': orders,
        'order_id': order_id
        
    }
    return render(request, "market/orderdetails.html", context)


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
    print(request.META['HTTP_REFERER'])
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
    

def designs(request):
    category = request.GET.get('cat')
    if category != None and ' ' in category:
        category = category.split(' ')
    if category != None:
        if type(category) == list:
            results = Design.objects.filter(categories__overlap = category).exclude(paused=True)
        else:
            results = Design.objects.filter(categories__contains = [category]).exclude(paused=True)
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
        context = {
            "user": User.objects.get(id = request.session['user_id']),
            "states": states
            }
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
    sales = OrderDetails.objects.filter(design_id=id)
    revenue = 0
    for sale in sales:
        revenue += sale.charged_price
    print(revenue)
    context = {
        'design': design,
        'cats': cats,
        'sales': sales,
        'revenue': revenue
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

def apply(request):
    return render(request, 'market/apply.html')

def logout(request):
    request.session.clear()
    return redirect('/')
    


