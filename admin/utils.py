# -*- coding: utf-8 -*-

import time
import json
import random
import datetime


def get_job_id():
    return str(int(time.time())) + str(random.randint(1, 99))


def get_json(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def load_json(x):
    return json.loads(x)


def get_now_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")