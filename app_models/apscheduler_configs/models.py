from django.db import models


class ApschedulerTasks(models.Model):
    job_id = models.CharField("任务job_id", max_length=255, blank=True, null=True, help_text="自动生成, 无需修改")
    description = models.CharField("任务名", max_length=255, blank=True, null=True)
    run_type = models.CharField("任务类型", max_length=255, default="python", choices=[
        ("api", "api"), ("python", "内部任务")
    ])
    task_func = models.CharField("脚本任务function名", max_length=255, blank=True, null=True)
    import_path = models.TextField("func路径或接口请求地址", blank=True, null=True, help_text="api填接口请求地址, 其余填function路径")
    api_method = models.CharField("接口请求方式", max_length=255, blank=True, null=True, default="post",
                                  choices=[("post", "post"), ("get", "get")])
    api_timeout = models.IntegerField("任务超时时间（单位：秒）", blank=True, null=True, default=600)
    args = models.TextField(blank=True, null=True)
    kwargs = models.TextField("任务参数", blank=True, null=True, help_text="参数, 填写json格式")
    status = models.IntegerField("任务状态", choices=[(1, "启动"), (0, "暂停")], default=1)
    trigger = models.CharField("定时类型", max_length=255, default="cron",
                               choices=[("date", "指定执行时间"), ("cron", "crontab"), ("interval", "interval")])
    second = models.CharField("秒", max_length=255, blank=True, null=True,
                              help_text="(0-59), 如果[定时类型]是[interval]时不填或填数字")
    minute = models.CharField("分", max_length=255, blank=True, null=True,
                              help_text="(0-59), 如果[定时类型]是[interval]时不填或填数字")
    hour = models.CharField("时", max_length=255, blank=True, null=True,
                            help_text="(0-23), 如果[定时类型]是[interval]时不填或填数字")
    day = models.CharField("天", max_length=255, blank=True, null=True,
                           help_text="day of month (1-31)")
    week = models.CharField("第几周", max_length=255, blank=True, null=True,
                            help_text="仅[定时类型]是[interval]时生效，不填或填数字")
    day_of_week = models.CharField(
        "周几", max_length=255, blank=True, null=True,
        choices=[("mon", "周一"), ("tue", "周二"), ("wed", "周三"), ("thu", "周四"), ("fri", "周五"), ("sat", "周六"), ("sun", "周日")]
    )
    start_date = models.DateField("任务开始日期", blank=True, null=True)
    end_date = models.DateField("任务结束日期", blank=True, null=True)
    next_run_time = models.DateTimeField("下次执行时间", blank=True, null=True,
                                         help_text="下次执行时间，如果[定时类型]是[指定执行时间]，那么运行时间在这里设置")
    is_delete = models.IntegerField(blank=True, null=True, default=0)
    create_time = models.DateTimeField("创建时间", blank=True, null=True, help_text="自动生成, 无需修改")
    update_time = models.DateTimeField("更新时间", blank=True, null=True, help_text="自动生成, 无需修改")

    class Meta:
        managed = False
        db_table = 'apscheduler_tasks'
        verbose_name = "任务调度通用配置"
        app_label = "apscheduler_configs"

