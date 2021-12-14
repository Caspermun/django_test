from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from blog.models import Category, Post, Author, Comment, User


def index(request):
    categories = Category.objects.all()
    authors = Author.objects.all()
    users = User.objects.all()
    try:
        category_fan = Category.objects.get(title='Fantastic')
    except ObjectDoesNotExist:
        raise ValueError('This category does not exist')
    return render(request, 'index.html', {'categories': categories,
                                          'fan': category_fan, 'authors': authors,
                                          'users': users})


def category(request, pk):
    posts = Post.objects.filter(category_id=pk)
    return render(request, 'category.html', locals())


def author(request, pk):
    posts = Post.objects.filter(author_id=pk)
    params = {'posts': posts}
    return render(request, 'author.html', params)


def user(request, pk):
    comments = Comment.objects.filter(users_id=pk)
    params = {'comments': comments}
    return render(request, 'user.html', params)