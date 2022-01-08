from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from blog.models import Category, Post, Author, Comment, CustomUser


def index(request):
    categories = Category.objects.all()
    authors = Author.objects.all()
    users = CustomUser.objects.all()

    user_list = []
    for i in users:
        comment = Comment.objects.filter(users_id=i.id)
        if comment:
            user_list.append(i.id)
    us = users.filter(id__in=user_list)

    return render(request, 'index.html', {'categories': categories,
                                          'authors': authors,
                                          'users': us})


def category(request, pk):
    categories = Category.objects.all()
    authors = Author.objects.all()
    users = CustomUser.objects.all()

    user_list = []
    for i in users:
        comment = Comment.objects.filter(users_id=i.id)
        if comment:
            user_list.append(i.id)
    us = users.filter(id__in=user_list)

    try:
        category_fan = Category.objects.get(title='Cars')
    except ObjectDoesNotExist:
        raise ValueError('This category does not exist')

    posts = Post.objects.filter(category_id=pk)
    return render(request, 'category.html', locals())


def author(request, pk):
    categories = Category.objects.all()
    authors = Author.objects.all()
    users = CustomUser.objects.all()

    user_list = []
    for i in users:
        comment = Comment.objects.filter(users_id=i.id)
        if comment:
            user_list.append(i.id)
    us = users.filter(id__in=user_list)

    posts = Post.objects.filter(author_id=pk)
    params = {'posts': posts}
    return render(request, 'author.html', locals())


def user(request, pk):
    categories = Category.objects.all()
    authors = Author.objects.all()
    users = CustomUser.objects.all()

    user_list = []
    for i in users:
        comment = Comment.objects.filter(users_id=i.id)
        if comment:
            user_list.append(i.id)
    us = users.filter(id__in=user_list)

    comments = Comment.objects.filter(users_id=pk)
    params = {'comments': comments}
    return render(request, 'user.html', locals())


def card(request):
    name = 'Nursultan Mirlanov'
    return render(request, 'card.html', locals())
