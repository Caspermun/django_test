from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from django.db import models
from django.core.files import File
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title')

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title')
    text = models.TextField(verbose_name='Text')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, verbose_name='Category')
    author = models.ForeignKey(to='Author', on_delete=models.CASCADE, verbose_name='Author', null=True)

    def __str__(self):
        return self.title


class Ad(models.Model):
    class Meta:
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
        ordering = ['-created_at']

    title = models.CharField(max_length=255, verbose_name='Title')
    description = models.TextField()
    image = models.ImageField(upload_to='ads/', verbose_name='Main image', null=True, blank=True)
    user = models.ForeignKey(to='CustomUser', on_delete=models.CASCADE, verbose_name='User')
    created_at = models.DateTimeField(auto_now_add=True)
    moderated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    price = models.PositiveIntegerField(blank=True, null=True, verbose_name='Price')
    discount = models.IntegerField(blank=True, null=True, verbose_name='Discount')

    def __str__(self):
        return self.title

    @property
    def get_price(self):
        if self.price and self.discount:
            price = self.price - (self.price * self.discount / 100)
        else:
            price = 'Договорная'
        return price

    def get_remote_image(self, url):
        if not self.image:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(url).read())
            img_temp.flush()
            self.image.save(f"image_{self.pk}.jpeg", File(img_temp))
        self.save()


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    surname = models.CharField(max_length=255, verbose_name='Surname')

    # posts = models.ForeignKey(to='Post', on_delete=models.CASCADE, related_name='Posts')

    def __str__(self):
        return f'{self.name} {self.surname}'

AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}

class CustomUser(AbstractUser):
    is_premium = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))

    def __str__(self):
        return self.username


    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class Comment(models.Model):
    comments = models.TextField(max_length=300, verbose_name='Comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    users = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='Users', null=True)

    def __str__(self):
        return self.comments
