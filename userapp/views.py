from django.conf import settings
from django.contrib import auth,messages
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render,redirect
from django.urls import reverse

from bookapp.models import Books
from django.contrib.auth.models import User
from userapp.models import Cart, CartItem
import stripe


# Create your views here.

def listBook(request):
    book = Books.objects.all()

    paginator = Paginator(book, 4)
    page_number = request.GET.get('page')

    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.page(page_number.num_pages)

    return render(request, 'user/userlistbook.html', {'book': book, 'page': page})

def detailsView(request, book_id):
    book = Books.objects.get(id=book_id)
    return render(request, 'user/userdetailsbook.html', {'book': book})

def Search_Book(request):
    query = None
    books = None

    if 'q' in request.GET:

        query = request.GET.get('q')
        books = Books.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))

    else:
        books = []

    context = {'books': books, 'query': query}

    return render(request, 'user/usersearch.html', context)

def Register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('password1')

        if password == cpassword:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'This username already exist')
                return redirect('user/register.html')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'This mail already taken')
                return redirect('user/register.html')
            else:
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                                email=email, password=password)
                user.save()
            return redirect('login')
        else:
            messages.info(request, 'Password not maching')
            return redirect('register')

    return render(request, 'user/register.html')


def loginUser(request):

    if request.method=='POST':
        username=request.POST.get('username')
        password = request.POST.get('password')
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Please provide correct details')
            return redirect('login')

    return render(request, 'user/login.html')

def logOut(request):
    auth.logout(request)
    return redirect('login')


def HomePage(request):

    return render(request,'user/home.html')

def add_to_cart(request, book_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        book = Books.objects.get(id=book_id)
    except Books.DoesNotExist:
        raise Http404("Book not found")

    if book.quantity > 0:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart,book=book)

        if not item_created:
            cart_item.quantity += 1
            cart_item.save()

    return redirect('viewcart')


def view_cart(request):
    cart,created=Cart.objects.get_or_create(user=request.user)
    cart_items=cart.cartitem_set.all()
    cart_item=CartItem.objects.all()
    total_price=sum(item.book.price * item.quantity for item in cart_items)
    total_items=cart_items.count()

    context={'cart_items':cart_items,'cart_item':cart_item,'total_price':total_price,'total_items':total_items}

    return render(request,'user/cart.html',context)

def increase_quantity(request,item_id):
    cart_item=CartItem.objects.get(id=item_id)
    if cart_item.quantity < cart_item.book.quantity:

        cart_item.quantity +=1
        cart_item.save()

    return redirect('viewcart')

def decrease_quantity(request,item_id):
    cart_item = CartItem.objects.get(id=item_id)
    if cart_item.quantity >1:

        cart_item.quantity -= 1
        cart_item.save()

    return redirect('viewcart')

def remove_from_cart(request,item_id):

    try:

        cart_item=CartItem.objects.get(id=item_id)
        cart_item.delete()

    except cart_item.DoesNotExist:
        pass

    return redirect('viewcart')

def create_checkout_session(request):
    cart_items=CartItem.objects.all()

    if cart_items:
        stripe.api_key=settings.STRIPE_SECRET_KEY

        if request.method=='POST':

            line_items=[]
            for cart_item in cart_items:
                if cart_item.book:
                    line_item={
                        'price_data':{
                            'currency':'INR',
                            'unit_amount':int(cart_item.book.price * 100),
                            'product_data':{
                                'name':cart_item.book.title
                            },
                        },
                        'quantity':1
                    }
                    line_items.append(line_item)

            if line_item:

                   checkout_session=stripe.checkout.Session.create(
                       payment_method_types=['card'],
                       line_items=line_items,
                       mode='payment',
                       success_url=request.build_absolute_uri(reverse('success')),
                       cancel_url=request.build_absolute_uri(reverse('cancel'))


                   )

                   return redirect(checkout_session.url,code=303)


def success(request):
    cart_items=CartItem.objects.all()
    for cart_item in cart_items:
        product=cart_item.book
        if product.quantity >=cart_item.quantity:
            product.quantity-=cart_item.quantity
            product.save()

    cart_items.delete()

    return render(request,'user/success.html')

def cancel(request):
    return render(request,'user/cancel.html')