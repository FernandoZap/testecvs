# -*- coding: utf-8 -*-
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model
from .forms import RegisterForm
from .models import User
from django.contrib.auth import login

User = get_user_model()


def register(request):
        template_name = 'accounts/register.html'
        if request.method =='POST':
                form = RegisterForm(request.POST)
                if form.is_valid():
                        form.save()
                        return redirect(settings.LOGIN_URL)
        else:
                form = RegisterForm()
        context = {
                'form': form
        }
        return render(request, template_name, context)


def tempo(requeste):
    return HttpResponse("<h1>tempo</h1>")


def incluirUser(request):
        vet =  list(range(56))
        #vet[1]={'username':'fernando.paz','senha':'dvs2@3@QWE','iduser':'166','email':'fernando.paz@joaobarbosaadvass.com.br'}
        vet[2]={'username':'bruna.dias','senha':'a2p8f4@','iduser':'213','email':'bruna.dias@joaobarbosaadvass.com.br'}
        vet[3]={'username':'higordamasceno','senha':'d@mascen0','iduser':'406','email':'higordamasceno@joaobarbosaadvass.com.br'}
        vet[4]={'username':'thiagosilva','senha':'Scxcasip1','iduser':'466','email':'thiagosilva@joaobarbosaadvass.com.br'}
        u1=User.objects.create_user(username='bruna.dias', email='bruna.dias@gmail.com',password='a2p8f4@', iduser='213')
        u1.save()


        """
        for k in range(2,5):
                u1=User.objects.create_user(username=vet[k]['username'], email=vet[k]['email'],password=vet[k]['senha'], iduser=vet[k]['iduser'])
                u1.save()
        """
        return HttpResponse("<h1>tempo</h1>")

