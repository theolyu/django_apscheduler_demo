# -*- coding: utf-8 -*-

import requests
from library.instance import logger


def test_log(info=False, error=False, warning=False, error_raise=False):
    if info:
        logger.info("test_info")
    if error:
        logger.error("test_error")
    if warning:
        logger.warning("test_warning")
    if error_raise:
        logger.error("test_error_raise")
        raise ValueError("test_error_raise")


def base_requests(url, timeout=600, method="get", **kwargs):
    method = str(method).lower()

    if method == "get":
        response = requests.get(url=url, params=kwargs, timeout=timeout)
        if response.status_code == 200:
            pass
        else:
            logger.error("接口: {url} 无法连接: status_code: {status_code}".format(url=url, status_code=response.status_code))
            raise ValueError("接口: {url}, 状态码: {status_code}".format(url=url, status_code=response.status_code))
    elif method == "post":
        response = requests.post(url=url, json=kwargs, timeout=timeout)
        if response.status_code == 200:
            response = response.json()
            code = response.get("code", None)
            if code is not None:
                if code == 200:
                    pass
                else:
                    raise ValueError("接口: {url}; ERROR: {error}\n traceback: {traceback}".format(
                        url=url, error=response.get("msg", "error"), traceback=response.get("traceback", "traceback")
                    ))
            else:
                pass
        else:
            logger.error("接口: {url} 无法连接: status_code: {status_code}".format(url=url, status_code=response.status_code))
            raise ValueError("接口: {url} 无法连接, 状态码: {status_code}".format(url=url, status_code=response.status_code))
    else:
        raise ValueError("method is error")
