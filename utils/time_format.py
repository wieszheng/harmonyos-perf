# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 00:48
@Author   : wieszheng
@Software : PyCharm
"""

import time
from datetime import datetime


def get_str_times(time_type='%H:%M:%S') -> str:
    """
    获取当前时间 格式13:28:53
    :param time_type:
    :return:
    """
    ret_time = datetime.now().strftime(time_type)
    return ret_time


def get_str_day_times(time_type='%H:%M:%S_%d') -> str:
    """
    获取当前时间 13:28:53_10
    :return:
    """
    ret_time = datetime.now().strftime(time_type)
    return ret_time


def get_str_date(time_type='%Y/%m/%d') -> str:
    """
    获取当前日期 2022/12/10
    :return:
    """
    ret_time = datetime.now().strftime(time_type)
    return ret_time


def ret_pc_device_diff_value(times) -> int:
    """
    获取当前时间戳 相差时间戳
    :param times: 13:28:53
    :return:
    """
    device_times = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ' ' + times
    diff_value = int(time.time()) - date_to_strptime(device_times) / 1000 - 1
    return int(diff_value)


def get_str_detail_time() -> str:
    """
    获取当前详细时间 2022/12/10 13:28:53
    :return:
    """
    ret_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    return ret_time


def date_to_strptime(datetimes) -> int:
    """
    时间转换成时间戳
    :param datetimes: 2022-12-10 13:28:53
    :return:
    """
    timeArray = time.strptime(datetimes, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(timeArray)) * 1000


#
def get_str_detail_time_logfile() -> str:
    """
    获取当前详细时间，用于文件或文件夹创建  格式2022_12_10_13_40_29
    :return:
    """
    ret_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    return ret_time


def get_str_detail_time_raphaelfile() -> str:
    """
    获取当前详细时间，用于文件或文件夹创建  格式13_40_29
    :return:
    """
    ret_time = datetime.now().strftime('%H_%M_%S')
    return ret_time


def check_time_interval(base_time, interval, time_type='s') -> bool:
    """
    检查时间间隔
    :param base_time: 13:28:53
    :param interval: 间隔时间
    :param time_type: 时间类型 s:秒 h:小时 m:分钟
    :return:
    """
    now_time = int(time.time())
    compare_interval = interval
    if time_type == 'h':
        compare_interval = interval * 60 * 60
    elif time_type == 'm':
        compare_interval = interval * 60

    if now_time - base_time > compare_interval:
        return True
    else:
        return False
