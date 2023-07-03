import os

#SECRET_KEY = 'django-insecure-f$7k1%q(8-&l9k6$vj5u8y%i7pb^3qa%1ng^_v75u@g7@3ymnm'

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_civitas',
        'USER': 'root',
        'PASSWORD': 'dvs2#3$MYSQL',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
