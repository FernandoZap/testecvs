from  django.urls import include, path
from django.contrib import admin
from . import views as v1

app_name = 'core'

urlpatterns = [
    path('', v1.home, name='home'),
    
]
