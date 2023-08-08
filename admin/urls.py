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

admin.site.site_header = 'DjangoApschedulerDemo'
admin.site.index_title = 'TestDjangoApschedulerDemoSystem'
admin.site.site_title = "DjangoApschedulerDemo V1.0"

urlpatterns = [
                  path('', views.index),
                  path('admin/', admin.site.urls),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from admin.views import get_tasks, get_existed_jobs, scheduler

status_tasks, status_tasks_ids = get_tasks(is_status=True)
pause_tasks, pause_tasks_ids = get_tasks(is_status=False)
existed_jobs_ids = get_existed_jobs(scheduler=scheduler)

for pause_id in set(existed_jobs_ids) & set(pause_tasks_ids):
    scheduler.pause_job(job_id=pause_id)

for status_id in set(existed_jobs_ids) & set(status_tasks_ids):
    scheduler.resume_job(job_id=status_id)

for remove_id in set(existed_jobs_ids) - set(status_tasks_ids + pause_tasks_ids):
    scheduler.remove_job(remove_id)

for add_id in set(status_tasks_ids + pause_tasks_ids) - set(existed_jobs_ids):
    # add_jobs()
    ## 当前机制下, 服务停止时不能新建任务, 所以重启时不考虑add
    pass