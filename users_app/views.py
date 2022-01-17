# coding=utf-8
import json
import threading
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response
from django.contrib.auth.views import logout
from django.template import loader
from django.urls import reverse

from categories.views import generate_view_params
from .forms import LoginForm, RegisterForm, SetPasswordForm, SetUserInfoForm, ChangePasswordForm
from .models import Users
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from Classified.parameters import SITE_PROTOCOL, SITE_URL, ADMIN_EMAIL
import requests
import hashlib


# Create your views here.


def users_logout(request):
    logout(request)
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET.get('next'))
    return HttpResponseRedirect(reverse('index'))


def users_login(request):
    login_form = LoginForm(request.POST)
    if request.POST:
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')

            if email and password:
                user = authenticate(email=email, password=password)
                if user is None:
                    return JsonResponse(dict(success=False, message='Неправильный логин или пароль'))
                else:
                    if not user.is_active:
                        return JsonResponse(dict(success=False, message='Ваш аккаунт был заблокирован'))
                    else:
                        login(request, user)
                        return JsonResponse(dict(success=True, message='login'))
        else:
            return JsonResponse(dict(success=False, message=str(login_form.errors)))
    return JsonResponse(dict(success=False, message='Запрос должен быть POST'))


def users_register(request):
    register_form = RegisterForm(request.POST)
    if request.POST:
        if register_form.is_valid():
            email = register_form.cleaned_data['email']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            try:
                user = Users.objects.get(email=email)
                return JsonResponse(dict(
                    success=False,
                    message='Этот пользователь уже существует. Пользователь зарегистрирован %s' % str(user.date_joined)
                ))
            except ObjectDoesNotExist:
                if password1 and password2 and password1 == password2:
                    user = Users(
                        email=email,
                        password=make_password(password1),
                        date_joined=datetime.now(),
                        is_active=True,
                        is_staff=True
                    )
                    user.save()
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    _password = urlsafe_base64_encode(password1)

                    template = loader.get_template('app/partial/confirm_email.html')
                    contexts = {
                        'link': SITE_PROTOCOL + SITE_URL + reverse('users:users_confirm',
                                                                   kwargs={'uidb64': uid, 'token': token,
                                                                           'password': _password})
                    }
                    print contexts
                    response = template.render(contexts, request)
                    thread = threading.Thread(
                        target=user.email_user,
                        args=(
                            u'Активация пользователя | TumaR24',
                            response
                        )
                    )
                    thread.start()
                    return JsonResponse(dict(
                        success=True,
                        message='register'
                    ))
        else:
            return JsonResponse(dict(success=False, message=str(register_form.errors)))
    return JsonResponse(dict(success=False, message='Запрос должен быть POST'))


email_confirm_messages = {
    'inactive': 'inactive_error',
    'invalid': 'invalid_user_data',
    'does_not_exists': 'user_does_not_exists',
    'invalid_data': 'invalid_token_or_uidb64',
    'deprecated_token': 'deprecated_user_token'
}


def users_email_confirm(request, uidb64, token, password):
    if uidb64 is not None and token is not None:
        uid = urlsafe_base64_decode(uidb64)
        password = urlsafe_base64_decode(password)
        try:
            user = Users.objects.get(pk=uid)
            if user.email_token != token:
                if default_token_generator.check_token(user, token):
                    user_cache = authenticate(email=user.email, password=password)
                    if user_cache is not None:
                        if user_cache.is_active:
                            login(request, user_cache)
                            user.email_token = token
                            user.save()

                            return HttpResponseRedirect(
                                reverse('users:users_confirm_result', kwargs={'success': True})
                            )
                        else:
                            return HttpResponseRedirect(
                                reverse('users:users_confirm_result', kwargs={'success': False}) + '?message=' +
                                email_confirm_messages['inactive']
                            )
                    return HttpResponseRedirect(
                        reverse('users:users_confirm_result', kwargs={'success': False}) + '?message=' +
                        email_confirm_messages['invalid']
                    )
            return HttpResponseRedirect(
                reverse('users:users_confirm_result', kwargs={'success': False}) + '?message=' +
                email_confirm_messages['deprecated_token']
            )
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('users:users_confirm_result', kwargs={'success': False}) + '?message=' + email_confirm_messages[
                    'does_not_exists']
            )
    return HttpResponseRedirect(
        reverse('users:users_confirm_result', kwargs={'success': False}) + '?message=' + email_confirm_messages[
            'invalid_data']
    )


def users_email_confirm_result(request, success):
    params = dict()
    params.update(generate_view_params(request))
    if success == 'True':
        params['success'] = True
        params['form'] = form = SetUserInfoForm(request.POST)
        if request.POST:
            if form.is_valid():
                user = Users.objects.get(email=request.user.email)
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                params['message'] = u'Информация успешно сохранена'
    else:
        message = request.GET.get('message')
        temp_params = {
            'success': False
        }
        if message == email_confirm_messages['inactive']:
            temp_params['message'] = u'Ваш пользователь был заблокирован<br>Обратитесь к администраторам: ' \
                                     u'<a href="mailto:' + ADMIN_EMAIL[0] + u'">' + ADMIN_EMAIL[0] + u'</a>'
            temp_params['reason'] = 'inactive'
        if message == email_confirm_messages['invalid']:
            temp_params['message'] = u'Мы не смогли вас авторизовать, пожалуйста авторизуйтесь'
            temp_params['form'] = LoginForm
            temp_params['reason'] = 'invalid'
        if message == email_confirm_messages['does_not_exists']:
            temp_params['message'] = u'Мы не смогли найти этого пользователя, попробуйте зарегистрироваться заново'
            temp_params['form'] = RegisterForm
            temp_params['reason'] = 'does_not_exists'
        if message == email_confirm_messages['invalid_data']:
            temp_params['message'] = u'Данные для активации аккаунта неправильные'
            temp_params['reason'] = 'invalid_data'
        if message == email_confirm_messages['deprecated_token']:
            temp_params['message'] = u'Ссылка на активацию вашего аккаунта устарела'
            temp_params['reason'] = 'deprecated_token'
        params.update(temp_params)

    return render(request, 'app/email_verify.html', params)


@login_required
def set_user_password(request):
    form = SetPasswordForm(request.POST)
    params = {
        'set_password_form': form
    }
    if request.POST:
        if form.is_valid():
            pass1 = form.cleaned_data['password1']
            pass2 = form.cleaned_data['password2']

            if pass1 and pass2 and pass1 == pass2:
                try:
                    current_user = Users.objects.get(email=request.user.email)
                    current_user.password = make_password(pass1)
                    current_user.save()
                    user = authenticate(email=current_user.email, password=pass1)
                    login(request, user)
                    params.update(dict(result=True, message='Ваш пароль успешно изменен!'))
                except ObjectDoesNotExist:
                    params.update(dict(result=False, message='Мы не нашли пользователя'))
            else:
                params.update(dict(result=False, message='Пароли не сопадают'))
    params.update(generate_view_params(request))
    return render(request, 'app/partial/set_password.html', params)


# https://oauth.vk.com/authorize?scope=email&state=ROB8bYW1kwyV&redirect_uri=http%3A%2F%2Fwww.tumar24.ru%2Faccounts%2Fvk%2Flogin%2Fcallback%2F&response_type=code&client_id=6011425


def vk_auth(request):
    state = 'ROB8bYW1kwyV'
    request.COOKIES['vk_auth_state'] = state
    redirect_url = SITE_PROTOCOL + SITE_URL + reverse('users:vk_login_response')
    link = 'https://oauth.vk.com/authorize?scope=email&display=page&response_type=code&client_id=6011425&state=' + state + '&redirect_uri=' + redirect_url
    return HttpResponseRedirect(link)


def vk_auth_response(request):
    client_id = '6011425'
    client_secret = 'qhmMuiiiCFnMVQWOClJs'
    params = {

    }
    params.update(generate_view_params(request))
    if 'code' in request.GET:
        code = request.GET.get('code')
        vk_user = requests.get(
            'https://oauth.vk.com/access_token?client_id=' + client_id + '&client_secret=' + client_secret + '&code=' + code + '&redirect_uri=' + SITE_PROTOCOL + SITE_URL + reverse(
                'users:vk_login_response'))
        try:
            response = json.loads(vk_user.content)
        except:
            response = None
        if 'access_token' in response:
            if 'email' in response:
                token = response['access_token']
                vk_user_id = response['user_id']
                vk_user_email = response['email']
                vk_user = requests.get('https://api.vk.com/method/users.get?user_ids=' + str(
                    vk_user_id) + '&fields=first_name,last_name,&access_token=' + token)
                response = json.loads(vk_user.content)
                is_first_name_contains = response['response'][0].get('first_name', False)
                if is_first_name_contains and vk_user_email:
                    try:
                        t_user = Users.objects.get(email=vk_user_email)
                        login(request, t_user)
                        if not t_user.password:
                            return HttpResponseRedirect(reverse('users:users_set_password'))
                        return HttpResponseRedirect(reverse('index'))
                    except ObjectDoesNotExist:
                        new_user = Users()
                        new_user.email = vk_user_email
                        new_user.first_name = response['response'][0].get('first_name')
                        new_user.last_name = response['response'][0].get('last_name')
                        new_user.date_joined = datetime.today()
                        new_user.save()
                        login(request, new_user)
                        return HttpResponseRedirect(reverse('users:users_set_password'))
            else:
                params['message'] = u'У вас не привязан Email, пожалуйста зарегистрируйтесь у нас на сайте'
    return render(request, 'app/login_error.html', params)


def ok_auth(request):
    app_id = '1251005440'
    redirect_url = SITE_PROTOCOL + SITE_URL + reverse('users:ok_auth_response')
    link = 'http://www.ok.ru/oauth/authorize?client_id=' + app_id + '&response_type=code&redirect_uri=' + redirect_url + '&scope=GET_EMAIL;VALUABLE_ACCESS'
    return HttpResponseRedirect(link)
    # params = {
    #     'reason': 'ok.ru'
    # }
    # params.update(generate_view_params(request))
    # return render(request, 'app/login_error.html', params)


def ok_auth_response(request):
    app_id = '1251005440'
    app_secret = 'DF50C0D03A0A1DCF207C27CF'
    app_public = 'CBAFNBJLEBABABABA'
    if 'code' in request.GET:
        code = request.GET.get('code', 'None')
        redirect_url = SITE_PROTOCOL + SITE_URL + reverse('users:ok_auth_response')
        r = requests.post('http://api.ok.ru/oauth/token.do', {
            'code': code,
            'redirect_uri': redirect_url,
            'grant_type': 'authorization_code',
            'client_id': app_id,
            'client_secret': app_secret
        })
        try:
            access_token = json.loads(r.content).get('access_token')
        except:
            access_token = None
        if access_token:
            sign = hashlib.md5('application_key=' + app_public + 'method=users.getCurrentUser' + hashlib.md5(
                access_token + app_secret).hexdigest()).hexdigest()
            ok_user_data = requests.get(
                'http://api.ok.ru/fb.do?method=users.getCurrentUser&access_token=' + access_token + '&application_key=' + app_public + '&sig=' + sign)
            try:
                ok_user_data = json.loads(ok_user_data.content)
            except:
                ok_user_data = dict()
            if 'email' in ok_user_data:
                try:
                    t_user = Users.objects.get(email=ok_user_data['email'])
                    login(request, t_user)
                    if not t_user.password:
                        return HttpResponseRedirect(reverse('users:users_set_password'))
                    return HttpResponseRedirect(reverse('index'))
                except ObjectDoesNotExist:
                    new_user = Users()
                    new_user.email = ok_user_data['email']
                    new_user.first_name = ok_user_data['first_name']
                    new_user.last_name = ok_user_data['last_name']
                    new_user.date_joined = datetime.today()
                    new_user.save()
                    login(request, new_user)
                    return HttpResponseRedirect(reverse('users:users_set_password'))
    return render(request, 'app/login_error.html', generate_view_params(request))


# https://www.facebook.com/dialog/oauth?client_id={client_id}&redirect_uri=mysite.com/fblogin&response_type=code

def fb_auth(request):
    fb_client_id = '1881419722139777'
    redirect_url = SITE_PROTOCOL + SITE_URL + reverse('users:fb_auth_response')
    link = 'https://www.fb.com/dialog/oauth?client_id=' + fb_client_id + '&redirect_uri=' + redirect_url + '&response_type=code'
    return HttpResponseRedirect(link)


def fb_auth_response(request):
    fb_client_id = '1881419722139777'
    fb_client_secret = '9a099b51a1d30fcb822bddf7f2a1307a'
    if 'code' in request.GET:
        code = request.GET.get('code', 'None')
        redirect_url = SITE_PROTOCOL + SITE_URL + reverse('users:fb_auth_response')
        get_access_token = requests.get(
            'https://graph.facebook.com/oauth/access_token?client_id=' + fb_client_id + '&redirect_uri=' + redirect_url + '&client_secret=' + fb_client_secret + '&code=' + code)
        try:
            r = json.loads(get_access_token.content)
        except:
            r = dict()
        if 'access_token' in r:
            fb_user = requests.get(
                'https://graph.facebook.com/me?access_token=' + r[
                    'access_token'] + '&fields=email,first_name,last_name')
            fb_user_data = json.loads(fb_user.content)
            if 'email' in fb_user_data:
                fb_user_email = fb_user_data.get('email')
                try:
                    t_user = Users.objects.get(email=fb_user_email)
                    login(request, t_user)
                    if not t_user.password:
                        return HttpResponseRedirect(reverse('users:users_set_password'))
                    return HttpResponseRedirect(reverse('index'))
                except ObjectDoesNotExist:
                    new_user = Users()
                    new_user.email = fb_user_email
                    new_user.first_name = fb_user_data.get('first_name')
                    new_user.last_name = fb_user_data.get('last_name')
                    new_user.date_joined = datetime.today()
                    new_user.save()
                    login(request, new_user)
                    return HttpResponseRedirect(reverse('users:users_set_password'))
    return render(request, 'app/login_error.html', generate_view_params(request))


def profile(request, user_id):
    try:
        user = Users.objects.get(id=user_id)
        params = {
            'user': user,
            'change_password_form': ChangePasswordForm(request.POST)
        }
        params.update(generate_view_params(request))
        return render(request, 'app/user_profile.html', params)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('exception:not_found'))


@login_required
def change_password(request):
    form = ChangePasswordForm(request.POST)
    if request.POST:
        if form.is_valid():
            old_pass = form.cleaned_data['old_password']
            user = authenticate(email=request.user.email, password=old_pass)
            pass1 = form.cleaned_data['new_password']
            pass2 = form.cleaned_data['confirm_new_password']
            if user:
                if pass1 and pass2 and pass1 == pass2:
                    user.password = make_password(pass1)
                    user.save()
                    login(request, user)
                    return JsonResponse(dict(success=True))
                return JsonResponse(dict(success=False, message='Пароли введены не верно или вообще не введены'))
            return JsonResponse(dict(success=False, message='Неправильно набран старый пароль'))
        return JsonResponse(dict(success=False, message='Форма не валидна'))
    return JsonResponse(dict(success=False, message='Запрос не защищён'))
