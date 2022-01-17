# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Users(AbstractUser):
    email = models.EmailField(verbose_name='Email', unique=True)
    username = models.CharField(verbose_name='Логин', null=True, blank=True, max_length=255)
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'
    email_token = models.CharField(max_length=255, verbose_name='Токен', null=True, blank=True)
