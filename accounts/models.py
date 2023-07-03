import re
from django.db import models
from django.core import validators
from django.core.validators import MinValueValidator
from django.contrib.auth.models import (AbstractBaseUser,PermissionsMixin,
        UserManager)

class User(AbstractBaseUser,PermissionsMixin):
        FUNCAO_CHOICES = (
                ('SUP','Adv. Supervisor'),
                ('INT','Adv. Interno'),
                ('EAJ','Estagiário Jurídico'),
                ('EAD','Estagiario Administrativo'),
                ('FUN','Funcionário'),

                )
        username = models.CharField('Nome de usuário',
         max_length=30,
         unique=True,
         validators = [validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                'O nome do usuário somente pode conter letras, dígitos numéricos e os seguintes caracteres:',
                'inválido')]
        )
        email = models.EmailField('E-mail', unique=True)
        name = models.CharField('Nome', max_length=100,blank=True)
        funcao  = models.CharField('Função', max_length=25, choices = FUNCAO_CHOICES, default = 'Estagiario',)
        iduser = models.PositiveIntegerField('Id origem',default=0)
        is_active = models.BooleanField('Está ativo?',blank=True,default=True)
        is_staff = models.BooleanField('É da equipe', blank=True, default=False)
        date_joined = models.DateTimeField('Data de entrada',auto_now_add=True)

        objects = UserManager()

        USERNAME_FIELD = 'username'
        REQUIRED_FIELDS = ['email']

        def __str__(self):
                return self.name or self.username

        def get_short_name(self):
                return self.username

        def get_full_name(self):
                return str(self)

        class Meta:
                verbose_name = 'Usuário'
                verbose_name_plural = 'Usuários'
