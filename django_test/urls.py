"""django_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from blog.api.v1.views import ListCreateAdView, RetrieveUpdateDestroyAdView

from blog.registration import registration, activate_user, logout_user, sign_in
from blog.views import index, category, author, user, card, create_ad, ad, ads, read_csv, UserAdListView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', index, name='index'),
                  path('category/<int:pk>', category, name='category'),
                  path('author/<int:pk>', author, name='author'),
                  path('user/<int:pk>', user, name='user'),
                  path('login/', sign_in, name='login'),
                  path('logout/', logout_user, name='logout_user'),
                  path('registration/', registration, name='registration'),
                  path('post/', card, name='post'),
                  path('create-ad/', create_ad, name='create_ad'),
                  path('ad/', ad, name='ad'),
                  path('ads/<int:pk>', ads, name='ads'),
                  path('ads/user/<int:pk>', UserAdListView.as_view(), name='user_ads'),
                  path('readcsv/', read_csv, name='parser'),
                  path('api/v1/get-ads/', ListCreateAdView.as_view(), name='get_list_ads'),
                  path('api/v1/get-ad/<int:pk>/', RetrieveUpdateDestroyAdView.as_view(), name='get_rud')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
