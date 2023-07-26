# -*- coding: utf-8 -*-
import datetime
import traceback

from app_models.apscheduler_configs.models import ApschedulerTasks


def task_name_dict():
    data = ApschedulerTasks.objects.values("job_id", "description")
    return {_['job_id']: _['description'] for _ in list(data)}


cron_time_keys = ["second", "minute", "hour", "day", "week", "day_of_week"]
interval_time_keys = ["second", "minute", "hour", "day", "week"]


def check_job_id_existed(job_id):
    tasks = ApschedulerTasks.objects.filter(is_delete=0).filter(job_id=job_id).first()
    if len(list(tasks.values("id"))) > 0:
        return True
    else:
        return False


from admin.views import add_jobs, scheduler
from admin.utils import load_json
def add_reset_tasks(form_data):
    job_id = form_data['job_id']
    time_keys = ["second", "minute", "hour", "day", "week", "day_of_week"]
    date_keys = ["start_date", "end_date"]
    datetime_keys = ["next_run_time"]
    _time_parmas = {}
    for key in time_keys:
        if form_data[key] is not None:
            _time_parmas[key] = form_data[key]
    for key in date_keys:
        if form_data[key] is not None:
            _time_parmas[key] = form_data[key].strftime("%Y-%m-%d")
    for key in datetime_keys:
        if form_data[key] is not None:
            _time_parmas[key] = form_data[key].strftime("%Y-%m-%d %H:%M:%S")

    kwargs = form_data["kwargs"]
    if isinstance(kwargs, str):
        kwargs = load_json(kwargs)

    data = {
        "job_id": job_id,
        "run_type": form_data['run_type'],
        "task_func": form_data["task_func"],
        "import_path": form_data["import_path"],
        "api_timeout": form_data["api_timeout"],
        "api_method": form_data["api_method"],
        "kwargs": kwargs,
        "trigger": form_data["trigger"],
        "description": form_data["description"],
        "status": form_data['status']
    }

    data = dict(data, **_time_parmas)
    # job_id 不存在 add
    if not check_job_id_existed(job_id):
        try:
            add_jobs(scheduler=scheduler, tasks=[data])
            return job_id
        except:
            print(traceback.format_exc())
            raise ValueError("新增任务失败")
    else:
        # job_id 存在 reset
        try:
            data = form_data.copy()
            for key in date_keys:
                if data[key] is not None:
                    data[key] = data[key].strftime("%Y-%m-%d")
            for key in datetime_keys:
                if data[key] is not None:
                    data[key] = data[key].strftime("%Y-%m-%d %H:%M:%S")
            for key in ["create_time", "update_time"]:
                if key in data:
                    del data[key]
            if "_state" in data:
                del data['_state']

            add_jobs(scheduler=scheduler, tasks=[data])
            if data['status'] == 0:
                scheduler.pause_job(job_id=job_id)

            return job_id
        except:
            print(traceback.format_exc())
            raise ValueError("重载任务失败")


def get_next_run_time(job_id):
    data = scheduler.get_job(job_id)
    if not data.empty:
        _ = data.to_dict("records")[0]
        return {str(_['id']): str(_['next_run_time'] + datetime.timedelta(hours=8)) if _['next_run_time'] is not None else "-"}
    else:
        return {}
