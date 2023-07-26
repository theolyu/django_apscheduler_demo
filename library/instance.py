# -*- coding: utf-8 -*-
import os
from loguru import logger


LOG_DEFAULT_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} - {file} - {level} - {message}"
log_path = os.path.dirname(os.path.dirname(__file__)) + "/log/"
os.makedirs(log_path, exist_ok=True)
trace = logger.add(log_path + "main.log", format=LOG_DEFAULT_FORMAT)
