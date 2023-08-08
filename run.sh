#!/bin/bash
python /home/DjangoApschedulerDemo/manage.py makemigrations
python /home/DjangoApschedulerDemo/manage.py migrate
python /home/DjangoApschedulerDemo/manage.py runserver 0.0.0.0:8000