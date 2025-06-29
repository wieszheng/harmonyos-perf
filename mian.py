# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/28 15:06
@Author   : wieszheng
@Software : PyCharm
"""
import os
from typing import List

from config.conf import ROOT_PATH
from core.hdc import HDC
from core.thread_mem_cpu import ThreadMemCPU
from scripts.wxy_dialogue import Dialogue
from utils import time_format


class wxy_main:
    def __init__(self):
        self.hdc = HDC()

        self.wxy_dialog = Dialogue(self.hdc, "文小言对话")

        self.hdc.driver.unlock()

        self.begin_str_time = time_format.get_str_detail_time_logfile()
        self.log_dir, self.log_mem_dir, self.log_cpu_dir, self.log_view_dir = self.create_log_dir(
            ['mem', 'cpu', 'view'])
        self.thread_mem_cpu = ThreadMemCPU(self.hdc, self.log_mem_dir, self.log_cpu_dir, self.log_view_dir)

    def create_log_dir(self, log_name_list: list) -> List:
        log_dir = os.path.join(ROOT_PATH, "log", self.begin_str_time)
        all_log_path_list = []
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            all_log_path_list.append(log_dir)
            for name in log_name_list:
                paths = os.path.join(log_dir, name)
                all_log_path_list.append(paths)
                os.makedirs(paths)
        return all_log_path_list

    def start_run(self):
        self.thread_mem_cpu.start_mem_cpu_thread()

    def stop_run(self):
        self.thread_mem_cpu.stop_mem_cpu_thread()

    def run(self):
        self.start_run()
        for name in ['r1_model', 'wx_model', 'auto_model']:
            self.wxy_dialog.set_model_name(name)
            self.wxy_dialog.run()
        self.stop_run()


if __name__ == '__main__':
    wxy_main().run()
