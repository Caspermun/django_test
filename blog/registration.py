import json
import threading
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse

from blog.forms import LoginForm
from blog.models import Category, Author, Comment, CustomUser
from blog.parameters import SITE_PROTOCOL, SITE_URL

from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

# from .utils import token_generator
from django_test.utils import token_generator


def sign_in(request):
    categories = Category.objects.all()
    authors = Author.objects.all()
    users = CustomUser.objects.all()

    user_list = []
    for i in users:
        comment = Comment.objects.filter(users_id=i.id)
        if comment:
            user_list.append(i.id)
    us = users.filter(id__in=user_list)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form,
                                          'categories': categories})


# def send_activation_email(user, request):
#     current_site = get_current_site(request)
#     email_subject = 'Activate your account'
#     email_body = render_to_string('authentication/activate.html', {
#         'user': user,
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': generate_token.make_token(user)
#     })
#
#     email = EmailMessage(subject=email_subject, body=email_body,
#                          from_email=settings.EMAIL_FROM_USER,
#                          to=[user.email]
#                          )
#
#     if not settings.TESTING:
#         EmailThread(email).start()

def registration(request):
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST}
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            user = CustomUser.objects.create_user(username=username, email=email, password=password2)
            user.set_password(password2)
            user.is_active = False
            user.save()

            uid64 = urlsafe_base64_encode(force_bytes(user.pk))

            domain = get_current_site(request).domain
            link = reverse('activate', kwargs={'uid64': uid64,
                                               'token': token_generator.make_token(user)})

            activate_url = 'http://' + domain + link

            email_body = 'Hi ' + user.username + \
                         '. Please use this link to verify your account\n' + activate_url

            email_subject = 'Activate your account'
            email = EmailMessage(
                email_subject,
                email_body,
                'emailcnfrm@gmail.com',
                [email],
            )
            email.send(fail_silently=False)
            messages.success(request, 'Account successfully created')
            return HttpResponse('User created successfully!')
        else:
            return HttpResponse('Passwords doesnt match each other!')
    return render(request, 'registration.html', {'categories': categories})


def email_verification(request, uidb64, token):
    try:
        id = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=id)

        if not account_activation_token.check_token(user, token):
            return redirect('login' + '?message=' + 'User already activated')

        if user.is_active:
            return redirect('login')
        user.is_active = True
        user.save()

        messages.success(request, 'Account activated successfully')
        return redirect('login')

    except Exception as ex:
        pass

    return redirect('login')