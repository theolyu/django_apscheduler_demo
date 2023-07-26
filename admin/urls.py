"""admin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

admin.site.site_header = 'TestSystem'
admin.site.index_title = 'TestSystem'
admin.site.site_title = "TestSystemV1.0"

urlpatterns = [
                  path('', views.index),
                  path('/', admin.site.urls),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from admin.views import get_tasks, get_existed_jobs, scheduler, remove_jobs
from app_models.apscheduler_configs.utils import add_reset_tasks

tasks, tasks_ids = get_tasks()
existed_jobs_ids = get_existed_jobs(scheduler=scheduler)
delete_ids = list(set(existed_jobs_ids) - set(tasks_ids))
remove_jobs(scheduler=scheduler, delete_ids=delete_ids)

resume_ids = list(set(existed_jobs_ids) & set(tasks_ids))
for resume_id in resume_ids:
    _tasks, _id = get_tasks(resume_id)
    if _tasks:
        _tasks = _tasks[0]
        add_reset_tasks(_tasks)
