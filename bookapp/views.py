from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from .models import Books
from django.shortcuts import render, redirect


# Create your views here.

def createBook(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        quantity = request.POST.get('quantity')
        books = Books(title=title, author=author, price=price, image=image, quantity=quantity)
        books.save()

    return render(request, 'admin/createbook.html')


def listBook(request):
    book = Books.objects.all()

    paginator = Paginator(book, 4)
    page_number = request.GET.get('page')

    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.page(page_number.num_pages)

    return render(request, 'admin/listbook.html', {'book': book, 'page': page})


def detailsView(request, book_id):
    book = Books.objects.get(id=book_id)
    return render(request, 'admin/detailsbook.html', {'book': book})


def updateBook(request, book_id):
    book = Books.objects.get(id=book_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        quantity = request.POST.get('quantity')
        book.title = title
        book.author = author
        book.price = price
        book.image = image
        book.quantity = quantity

        book.save()

        return redirect('/')
    return render(request, 'admin/updatebook.html', {'book': book})


def deleteView(request, book_id):
    book = Books.objects.get(id=book_id)
    if request.method == 'POST':
        book.delete()

        return redirect('/')
    return render(request, 'admin/deletebook.html', {'book': book})


def index(request):
    return render(request, 'admin/base.html')


def Search_Book(request):
    query = None
    books = None

    if 'q' in request.GET:

        query = request.GET.get('q')
        books = Books.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))

    else:
        books = []

    context = {'books': books, 'query': query}

    return render(request, 'admin/search.html', context)
