import traceback
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from .models import ApschedulerTasks
from .forms import ApschedulerTasksForms
from app_models.apscheduler_configs.utils import get_next_run_time, add_reset_tasks, cron_time_keys, interval_time_keys
from admin.views import run_job, scheduler, pause_job
from admin.utils import get_json, load_json


@admin.register(ApschedulerTasks)
class ApschedulerTasksAdmin(admin.ModelAdmin):
    form = ApschedulerTasksForms
    list_display = [
        'id', 'job_id', 'description', "status", "job_next_run_time", 'log_display',
        'run_type', 'task_func', 'api_method',
        'api_timeout',
        "trigger", "time_display",
        'import_path',
        "start_date", "end_date", "next_run_time", "create_time", "update_time"
    ]

    fields = [
        'job_id', 'description', 'run_type', 'import_path', 'task_func', 'api_method',
        'api_timeout', "status",
        "trigger",
        "second", "minute", "hour", "day", "week", "day_of_week",
        "kwargs",
        "start_date", "end_date", "next_run_time", "create_time", "update_time"
    ]

    list_filter = ['status', 'run_type']
    search_fields = ['description', 'task_func', 'job_id']

    ordering = ['-id']
    list_per_page = 10

    actions = ["delete_selected", "resart_tasks", "pause_tasks", "start_tasks", "run_tasks"]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        choices = self.get_action_choices(request)
        choices.pop(0)  # clear default choices
        action_form = self.action_form(auto_id=None)
        action_form.fields['action'].choices = choices
        action_form.fields['action'].initial = "run_tasks"
        return super(ApschedulerTasksAdmin, self).changelist_view(request, extra_context)

    def job_next_run_time(self, obj):
        job_id = str(obj.job_id)
        _dict = get_next_run_time(job_id=job_id)
        if len(_dict) > 0:
            return _dict.get(job_id, "-")
        else:
            return "-"
    job_next_run_time.short_description = "下次任务执行时间"

    def time_display(self, obj):
        trigger = obj.trigger
        if trigger == "date":
            return "执行时间: " + str(obj.next_run_time)
        elif trigger == "cron":
            return get_json({_: obj.__dict__[_] for _ in cron_time_keys if obj.__dict__[_] is not None and len(str(obj.__dict__[_])) > 0})
        elif trigger == "interval":
            return get_json({_ + "s": obj.__dict__[_] for _ in interval_time_keys if obj.__dict__[_] is not None and len(str(obj.__dict__[_])) > 0})
        else:
            return ""
    time_display.short_description = "执行时间设置"

    def log_display(self, obj):
        url = "/django_apscheduler/djangojobexecution/?q={job_id}".format(job_id=obj.job_id)  # 跳转的超链接
        url_text = "日志"  # 显示的文本
        return format_html(u'<a href="{}" target="_blank">{}</a>'.format(url, url_text))
    log_display.allow_tags = True
    log_display.short_description = "LOG"

    def run_tasks(self, request, queryset):
        success_tasks = []
        error_tasks = []
        for task in queryset:
            try:
                if task.job_id is None:
                    error_tasks.append(task.id)
                else:
                    run_job(scheduler, task.job_id)
                    success_tasks.append(task.id)
            except:
                print(traceback.format_exc())
                error_tasks.append(task.id)
        if len(error_tasks) > 0:
            self.message_user(request,
                              message="{} 执行任务请求失败".format(",".join([str(_) for _ in error_tasks])),
                              level=messages.ERROR)
        if len(success_tasks) > 0:
            self.message_user(request,
                              message="{} 执行任务请求成功".format(",".join([str(_) for _ in success_tasks])),
                              level=messages.INFO)
    run_tasks.short_description = _('执行任务')

    def resart_tasks(self, request, queryset):
        success_tasks = []
        error_tasks = []
        for task in queryset:
            try:
                if task.job_id is None:
                    error_tasks.append(task.id)
                else:
                    add_reset_tasks(task.__dict__)
                    success_tasks.append(task.id)
            except:
                print(traceback.format_exc())
                error_tasks.append(task.id)
        if len(error_tasks) > 0:
            self.message_user(request,
                              message="{} 重载任务请求失败".format(",".join([str(_) for _ in error_tasks])),
                              level=messages.ERROR)
        if len(success_tasks) > 0:
            self.message_user(request,
                              message="{} 重载任务请求成功".format(",".join([str(_) for _ in success_tasks])),
                              level=messages.INFO)
    resart_tasks.short_description = _('重载任务')

    def pause_tasks(self, request, queryset):
        success_tasks = []
        error_tasks = []
        for task in queryset:
            try:
                ApschedulerTasks.objects.filter(job_id=task.job_id).update(status=0)
                if task.job_id is not None:
                    pause_job(scheduler, task.job_id)
                success_tasks.append(task.id)
            except:
                print(traceback.format_exc())
                error_tasks.append(task.id)
        if len(error_tasks) > 0:
            self.message_user(request,
                              message="{} 暂停任务请求失败".format(",".join([str(_) for _ in error_tasks])),
                              level=messages.ERROR)
        if len(success_tasks) > 0:
            self.message_user(request,
                              message="{} 暂停任务请求成功".format(",".join([str(_) for _ in success_tasks])),
                              level=messages.INFO)
    pause_tasks.short_description = _('暂停任务')

    def start_tasks(self, request, queryset):
        success_tasks = []
        error_tasks = []
        for task in queryset:
            try:
                ApschedulerTasks.objects.filter(job_id=task.job_id).update(status=1)
                if task.job_id is not None:
                    scheduler.resume_job(job_id=task.job_id)
                success_tasks.append(task.id)
            except:
                print(traceback.format_exc())
                error_tasks.append(task.id)
        if len(error_tasks) > 0:
            self.message_user(request,
                              message="{} 启动任务请求失败".format(",".join([str(_) for _ in error_tasks])),
                              level=messages.ERROR)
        if len(success_tasks) > 0:
            self.message_user(request,
                              message="{} 启动任务请求成功".format(",".join([str(_) for _ in success_tasks])),
                              level=messages.INFO)
    start_tasks.short_description = _('启动任务')

    def delete_selected(self, request, queryset):
        success_tasks = []
        error_tasks = []
        for task in queryset:
            try:
                if task.job_id is None or len(str(task.job_id)) == 0:
                    ApschedulerTasks.objects.filter(job_id=task.job_id).delete()
                    success_tasks.append(task.id)
                else:
                    ApschedulerTasks.objects.filter(job_id=task.job_id).update(is_delete=1)
                    if task.job_id is not None:
                        scheduler.remove_job(job_id=task.job_id)
                    ApschedulerTasks.objects.filter(job_id=task.job_id).delete()
                    success_tasks.append(task.id)
            except:
                print(traceback.format_exc())
                error_tasks.append(task.id)
        if len(error_tasks) > 0:
            self.message_user(request,
                              message="{} 删除任务请求失败".format(",".join([str(_) for _ in error_tasks])),
                              level=messages.ERROR)
        if len(success_tasks) > 0:
            self.message_user(request,
                              message="{} 删除任务请求成功".format(",".join([str(_) for _ in success_tasks])),
                              level=messages.INFO)

    delete_selected.short_description = _('彻底删除任务')