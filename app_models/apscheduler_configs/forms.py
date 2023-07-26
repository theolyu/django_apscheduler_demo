# -*- coding: utf-8 -*-
import traceback
from django import forms
from django.core.exceptions import ValidationError
from app_models.apscheduler_configs.utils import add_reset_tasks, interval_time_keys, cron_time_keys
from admin.utils import get_job_id, get_json, get_now_time


class ApschedulerTasksForms(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ApschedulerTasksForms, self).__init__(*args, **kwargs)
        kwargs = self.instance.kwargs
        if kwargs is None or kwargs == "":
            self.initial['kwargs'] = get_json({})

        job_id = self.instance.job_id
        if job_id is None or job_id == "":
            self.initial['job_id'] = get_job_id()

    def clean(self):
        clean_data = self.cleaned_data

        if clean_data['trigger'] == "date":
            if clean_data['next_run_time'] is None or str(clean_data['next_run_time']) == "":
                raise ValidationError('指定时间执行必须填写[下次执行时间]')
        elif clean_data['trigger'] == "cron":
            flag = 0
            for key in cron_time_keys:
                if clean_data[key] is not None and len(str(clean_data[key])) > 0:
                    flag = 1
                    break
            if not flag:
                raise ValidationError('crontab 类型, 以下字段至少一个有值: [{}]'.format(",".join(cron_time_keys)))
        elif clean_data['trigger'] == "interval":
            flag = 0
            for key in interval_time_keys:
                if clean_data[key] is not None and len(str(clean_data[key])) > 0:
                    flag = 1
                    break
            if not flag:
                raise ValidationError('每隔一段时间执行 类型, 以下字段至少一个有值: [{}]'.format(",".join(interval_time_keys)))

        print(clean_data)
        try:
            self.cleaned_data['job_id'] = add_reset_tasks(clean_data)
            if self.cleaned_data['create_time'] is None or self.cleaned_data['create_time'] == "":
                self.cleaned_data['create_time'] = get_now_time()
            self.cleaned_data['update_time'] = get_now_time()
        except Exception as e:
            print(traceback.format_exc())
            raise ValidationError('保存任务失败\n' + traceback.format_exc())
