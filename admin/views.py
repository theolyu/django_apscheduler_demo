import json
import time
import traceback

from django.shortcuts import redirect

# 设置Django运行所依赖的环境
import os
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')
# 更新配置文件
import django
django.setup()


def index(request):
    if not request.user.is_authenticated:
        return redirect('/login/?next=%s' % request.path)
    else:
        return redirect('/')


import pandas as pd
import datetime

from .utils import get_job_id, load_json, get_json

replace_existing = True
base_requests_path = "app_models.apscheduler_configs.api_tasks"
base_requests_func = "base_requests"

from app_models.apscheduler_configs.models import ApschedulerTasks


def get_tasks(job_id=None, table_id=None, is_status=True):
    if job_id is None and table_id is None:
        tasks = ApschedulerTasks.objects.filter(is_delete=0).exclude(job_id='apscheduler_monitor')
    elif job_id is not None and table_id is None:
        tasks = ApschedulerTasks.objects.filter(is_delete=0).filter(job_id=job_id)
    elif job_id is None and table_id is not None:
        tasks = ApschedulerTasks.objects.filter(is_delete=0).filter(id=table_id)
    else:
        tasks = ApschedulerTasks.objects.filter(is_delete=0).filter(id=table_id).filter(job_id=job_id)
    if is_status:
        tasks = tasks.filter(status=1)

    tasks = pd.DataFrame(list(tasks.values()))
    if not tasks.empty:
        tasks['have_job_id'] = 1
        tasks.loc[tasks['job_id'].apply(lambda x: len(x) == 0), "have_job_id"] = 0
        tasks.loc[tasks['have_job_id'] == 0, "job_id"] = tasks.loc[tasks['have_job_id'] == 0, "id"].apply(
            lambda x: get_job_id()
        )
        tasks_ids = tasks['job_id'].unique().tolist()

        update_data = tasks.loc[tasks['have_job_id'] == 0, ["id", "job_id"]]
        for data in update_data.to_dict("records"):
            ApschedulerTasks.objects.get(id=data['id']).update(**{k: v for k, v in data.items() if k != "id"})

    else:
        tasks = pd.DataFrame(columns=["job_id"])
        tasks_ids = []
    return tasks.to_dict("records"), tasks_ids


def load_json_param(task, key):
    if task[key] is not None:
        try:
            return json.loads(task[key])
        except:
            return task[key]
    else:
        return None


def get_trigger_param(task, key):
    trigger = task['trigger']
    value = task[key]
    if value is not None:
        value = str(value)
        if len(value) > 0:
            if trigger == "interval":
                return int(value)
            else:
                return task[key]
    return None


def get_param(task, key):
    value = task[key]
    if value is not None:
        value = str(value)
        if len(value) > 0:
            return value
    return None


def get_existed_jobs(scheduler):
    existed_jobs_ids = scheduler.get_jobs()
    existed_jobs_ids = [_.id for _ in existed_jobs_ids]
    return existed_jobs_ids


def resume_jobs(scheduler, resume_ids):
    if len(resume_ids) > 0:
        for job_id in resume_ids:
            scheduler.resume_job(job_id)


def remove_jobs(scheduler, delete_ids):
    if len(delete_ids) > 0:
        for job_id in delete_ids:
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)


def add_job(scheduler, task):
    job_id = task['job_id']
    description = task['description']
    task_func = task['task_func'] if "task_func" in task else None
    import_path = task['import_path']
    args = load_json_param(task, 'args') if "args" in task else None
    kwargs = load_json_param(task, 'kwargs')
    trigger = task['trigger']
    second = get_trigger_param(task, "second") if "second" in task else None
    minute = get_trigger_param(task, "minute") if "minute" in task else None
    hour = get_trigger_param(task, "hour") if "hour" in task else None
    day = get_trigger_param(task, "day") if "day" in task else None
    week = get_trigger_param(task, "week") if "week" in task else None
    day_of_week = get_trigger_param(task, "day_of_week") if "day_of_week" in task else None
    month = get_trigger_param(task, "month") if "month" in task else None

    start_date = get_param(task, "start_date") if "start_date" in task else None
    end_date = get_param(task, "end_date") if "end_date" in task else None
    next_run_time = get_param(task, "next_run_time") if "next_run_time" in task else None

    func = import_path + ":" + task_func

    if args is None:
        args = []

    if trigger == "date":
        if job_id in get_existed_jobs(scheduler):
            scheduler.modify_job(
                job_id=job_id, name=description, func=func, args=args,
                kwargs=kwargs,
            )
            scheduler.reschedule_job(
                job_id=job_id, trigger=trigger, run_date=next_run_time
            )
        else:
            scheduler.add_job(
                id=job_id, name=description, func=func, trigger=trigger, run_date=next_run_time, args=args,
                kwargs=kwargs,
                replace_existing=replace_existing
            )
    elif trigger == "interval":
        interval_params = {
            "seconds": second, "minutes": minute, "hours": hour, "days": day, "weeks": week,
            "next_run_time": next_run_time, "start_date": start_date, "end_date": end_date
        }
        params = {}
        for key, value in interval_params.items():
            if value is not None and str(value).lower() not in ["null", 'none', 'nat', 'nan']:
                params[key] = value
        if job_id in get_existed_jobs(scheduler):
            scheduler.modify_job(
                job_id=job_id, name=description, func=func, targs=args, kwargs=kwargs,
            )
            scheduler.reschedule_job(
                job_id=job_id, trigger=trigger, **params
            )
        else:
            scheduler.add_job(
                id=job_id, name=description, func=func, trigger=trigger, args=args, kwargs=kwargs,
                replace_existing=replace_existing,
                **params
            )
    elif trigger == "cron":
        cron_params = {
            "second": second, "minute": minute, "hour": hour, "day": day, "week": week, "day_of_week": day_of_week,
            "month": month, "next_run_time": next_run_time, "start_date": start_date, "end_date": end_date
        }
        params = {}
        for key, value in cron_params.items():
            if value is not None and str(value).lower() not in ["null", 'none', 'nat', 'nan']:
                params[key] = value
        if job_id in get_existed_jobs(scheduler):
            scheduler.modify_job(
                job_id=job_id, name=description, func=func, args=args, kwargs=kwargs,
            )
            scheduler.reschedule_job(
                job_id=job_id, trigger=trigger, **params
            )
        else:
            scheduler.add_job(
                id=job_id, name=description, func=func, trigger=trigger, args=args, kwargs=kwargs,
                replace_existing=replace_existing,
                **params
            )


def add_api_jobs(scheduler, task):
    kwargs = json.loads(task['kwargs'])
    timeout = task.get("api_timeout", 600)
    url = task['import_path']
    method = task['api_method']
    task['task_func'] = base_requests_func
    task['import_path'] = base_requests_path
    kwargs['url'] = url
    kwargs['timeout'] = timeout
    kwargs['method'] = method

    task['kwargs'] = get_json(kwargs)
    add_job(scheduler=scheduler, task=task)


def add_jobs(scheduler, tasks):
    for task in tasks:
        if task['run_type'] == "python":
            add_job(scheduler=scheduler, task=task)
        elif task['run_type'] == "api":
            add_api_jobs(scheduler=scheduler, task=task)


def pause_job(scheduler, job_id):
    if job_id in get_existed_jobs(scheduler=scheduler):
        scheduler.pause_job(job_id=job_id)


def run_job(scheduler, job_id):
    from apscheduler.executors.base import run_job as aps_run_job
    from pytz import utc
    events = aps_run_job(scheduler.get_job(job_id), 'default', [datetime.datetime.now(utc)], __name__)
    # 处理结果
    for event in events:
        scheduler._dispatch_event(event)


from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events

job_defaults = {
    'coalesce': True,
    'max_instances': 1,
    'misfire_grace_time': 180
}

scheduler = BackgroundScheduler(timezone="Asia/Shanghai", job_defaults=job_defaults)
scheduler.add_jobstore(DjangoJobStore(), "default")

register_events(scheduler)

scheduler.start()
print("Scheduler started!")




