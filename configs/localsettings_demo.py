# -*- coding: utf-8 -*-

### django
"""
# 生成方式
python manage.py shell
from django.core.management.utils import get_random_secret_key
get_random_secret_key()
"""
SECRET_KEY = "xxxxxxxxxxxxxxxxxx"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_name',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'db_host',
        'PORT': 'db_port',
    }
}