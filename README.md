# django_apscheduler_demo

### 简介

在`django-apscheduler`基础上，增加一个任务管理页面，支持通过页面对python定时任务进行配置、管理和执行，并支持查看执行日志。

### 创建任务管理表
```mysql
CREATE TABLE `apscheduler_tasks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_id` varchar(255) NOT NULL DEFAULT '' COMMENT '任务job_id(唯一)，捆绑apscheduler',
  `description` varchar(255) DEFAULT NULL COMMENT '备注',
  `run_type` varchar(255) NOT NULL DEFAULT 'python' COMMENT 'python：执行项目内脚本；api：调外部接口',
  `task_func` varchar(255) DEFAULT '' COMMENT '脚本任务function名',
  `import_path` text COMMENT '项目内脚本任务路径（python） 或 外部接口地址（api）',
  `api_method` varchar(255) DEFAULT NULL COMMENT '调接口的方法：get 或 post',
  `api_timeout` int(11) DEFAULT NULL COMMENT '调接口最长等待时间，一般设置为任务执行时间（单位：秒），不设置默认10分钟（600s），最长不超过30分钟（1800s）',
  `args` longtext,
  `kwargs` longtext COMMENT '任务参数 或 接口json参数',
  `status` tinyint(2) NOT NULL DEFAULT '1' COMMENT '任务状态，1启动，0暂停',
  `trigger` varchar(255) NOT NULL DEFAULT 'cron' COMMENT 'date, interval 或 cron，默认cron',
  `second` varchar(255) DEFAULT NULL COMMENT 'second(0-59), trigger是interval时不填或填数字',
  `minute` varchar(255) DEFAULT NULL COMMENT 'minute (0-59), trigger是interval时不填或填数字',
  `hour` varchar(255) DEFAULT NULL COMMENT 'hour (0-23), trigger是interval时不填或填数字',
  `day` varchar(255) DEFAULT NULL COMMENT 'day of month (1-31)',
  `week` varchar(255) DEFAULT NULL COMMENT 'week, trigger是interval时不填或填数字',
  `day_of_week` varchar(255) DEFAULT NULL COMMENT 'number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)',
  `start_date` date DEFAULT NULL COMMENT '任务开始日期',
  `end_date` date DEFAULT NULL COMMENT '任务结束日期',
  `next_run_time` datetime DEFAULT NULL COMMENT '下次执行时间，如果trigger是date，那么运行时间在这里设置',
  `is_delete` tinyint(2) NOT NULL DEFAULT '0' COMMENT '是否已删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT COMMENT='apscheduler定时服务任务表';
```

### 启动
#### 直接启动Django
```
python manage runserver 0.0.0.0:8000
```

### Docker Run
```commandline
docker build -t ImageName:version .
docker run -d --name=django_apscheduler_demo -p 8000:8000 ImageName:version bash
```