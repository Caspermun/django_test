import csv
from io import BytesIO

import requests
import tempfile
from django.core import files
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from blog.forms import AdForm
from blog.models import Category, Post, Author, Comment, CustomUser, Ad


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


def create_ad(request):
    categories = Category.objects.all()

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AdForm(request.POST, request.FILES)
            if form.is_valid():
                cd = form.cleaned_data
                ad = Ad.objects.create(title=cd['title'], description=cd['description'], image=cd['image'],
                                       user=request.user)
                return HttpResponse('Ad sent successfully!')
        else:
            form = AdForm()
    else:
        return HttpResponse('Please login.')
    return render(request, 'ad.html', {'form': form,
                                       'categories': categories})


def ad(request):
    ads = Ad.objects.all()

    return render(request, 'ad_list.html', locals())


def ads(request, pk):
    advert = Ad.objects.get(pk=pk)

    return render(request, 'ad_detail.html', locals())


def search_ads(request):
    ads = request.GET.get()
    if ads:
        adverts = Ad.objects.filter(title__contains=ads)
    else:
        adverts = Ad.objects.all()
    return render(request, 'ad_detail.html', locals())


def read_csv(request):
    file = str(settings.BASE_DIR) + r'/blog/parser/10_pages.csv'
    with open(file, 'r', encoding='utf-8') as f:
        for i in csv.reader(f):
            if i:
                title = i[1]
                desc = i[3]
                user_id = 1
                image = i[4]
                ad = Ad.objects.filter(title=title).exists()
                if not ad:
                    ad = Ad.objects.create(title=title, description=desc, user_id=user_id)
                    if image:
                        ad.get_remote_image(image)

    return HttpResponse('Done!')
