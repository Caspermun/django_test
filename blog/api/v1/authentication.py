from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import views
from rest_framework.authentication import TokenAuthentication

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from blog.api.v1.serializers import RegisterSerializer, LoginSerializer
from blog.api.v1.utils import generate_token
from blog.models import CustomUser
from django_test import settings


class LoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        # serializer = LoginSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        data = request.data
        try:
            user = CustomUser.objects.get(email=data['email'])
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key if token else created.key})
        except:
            return Response({'error': 'no user'}, status=HTTP_404_NOT_FOUND)

    def get(self, token):
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')

class LoginTokenView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class RegisterView(views.APIView):

    def get(self, *args, **kwargs):
        return Response({'data': {
            'username': 'user',
            'email': 'email',
            'password': 'password',
            'password2': 'password2'

        }})

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            email_subject = 'Activate your account'
            email_body = render_to_string('authentification/activate.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            to_email = serializer.data['email']
            email = EmailMessage(subject=email_subject, body=email_body,
                                 from_email=settings.EMAIL_FROM_USER,
                                 to=[to_email]
                                 )
            email.send()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


def activation_user(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user and generate_token.check_token(user, token):
        user.is_verified = True
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
