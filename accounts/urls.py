from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_view
from .  import views as v2

app_name = 'accounts'


urlpatterns = [
    path('login', auth_view.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),
    path('logout', auth_view.LogoutView.as_view(
        template_name='accounts/login.html'
    ), name='logout'),

    path('tempo', v2.tempo, name='tempo'),
    path('incluirUser', v2.incluirUser, name='incluirUser'),


]
