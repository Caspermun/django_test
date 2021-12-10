from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from blog.models import Category, Post, Author


def index(request):
    categories = Category.objects.all()
    try:
        category_fan = Category.objects.get(title='Fantastic')
    except ObjectDoesNotExist:
        raise ValueError('This category does not exist')
    return render(request, 'index.html', {'categories': categories, 'fan': category_fan})

def index2(request):
    authors = Author.objects.all()
    try:
        author_nur = Author.objects.get(title='Nursultan')
    except ObjectDoesNotExist:
        raise ValueError('This author does not exist')
    return render(request, 'index.html', {'author': authors, 'nur': author_nur})


def category(request, pk):
    posts = Post.objects.filter(category_id=pk)
    return render(request, 'category.html', locals())


def author(request, pk):
    posts = Post.objects.filter(author_id=pk)
    return render(request, 'author.html', locals())

# def post(request, pk):
#     authors = Author.objects.filter(post_id=pk)
#     return render(request, 'post.html', locals())