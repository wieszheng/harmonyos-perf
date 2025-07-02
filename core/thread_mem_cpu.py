# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/28 00:12
@Author   : wieszheng
@Software : PyCharm
"""
import os
import threading

from typing import Any

from loguru import logger

from core.cpu import CpuMonitor
from core.memory import MemoryMonitor
from utils.render.render_chart import ChartRenderer


class ThreadMemCPU:
    def __init__(self, hdc: Any, log_mem_dir: str, log_cpu_dir: str, log_view_dir: str,
                 package_name: str = 'com.baidu.yiyan.ent'):
        self.hdc = hdc
        self.cpu_monitor = CpuMonitor(self.hdc.driver)
        self.mem_monitor = MemoryMonitor(self.hdc.driver)
        self.thread_flag = True
        self.log_mem_dir = log_mem_dir
        self.log_cpu_dir = log_cpu_dir
        self.log_view_dir = log_view_dir
        self.package_name = package_name

    def _thread_mem_cpu(self):
        """
        线程函数，用于监控内存和CPU使用率
        :return:
        """
        while self.thread_flag:
            package_name = "com.baidu.yiyan.ent"
            cpu_info = self.cpu_monitor.get_sp_daemon_cpu(package_name)
            mem_info = self.mem_monitor.get_sp_daemon_memory(package_name)
            self.write_mem_info(mem_info, package_name)
            self.write_cpu_info(cpu_info, package_name)
            logger.debug(f"CPU使用率: {cpu_info}")
            logger.debug(f"内存使用情况: {mem_info}")

    def start_mem_cpu_thread(self):
        """
        启动线程，用于监控内存和CPU使用率
        :return:
        """
        thread = threading.Thread(target=self._thread_mem_cpu)
        thread.start()

    def stop_mem_cpu_thread(self):
        """
        停止线程，用于监控内存和CPU使用率
        :return:
        """
        self.thread_flag = False

        chart_configs = [
            {'log_dir': self.log_mem_dir, 'chart_type': 'mem', 'title': '内存', 'decs': '内存使用率', 'unit': 'MB'},
            {'log_dir': self.log_cpu_dir, 'chart_type': 'cpu', 'title': 'CPU', 'decs': 'CPU使用率', 'unit': '%'}
        ]

        for cfg in chart_configs:
            self.generate_charts(**cfg)

    def write_mem_info(self, mem_detail: dict, package_name: str):
        """
        写入内存使用情况
        :param mem_detail:
        :param package_name:
        :return:
        """
        file_path = os.path.join(self.log_mem_dir, 'mem_{}_log.txt'.format(package_name))

        begin_line = ''
        mem_line = ''
        for mem_name, mem_data in mem_detail.items():
            begin_line = begin_line + mem_name.replace(' ', '') + ','
            mem_line = mem_line + str(mem_data) + ','

        if not os.path.exists(file_path):
            mem_log = open(file_path, 'a+')
            mem_log.write(begin_line + '\n')
            mem_log.write(mem_line + '\n')
            # self.mem_log_all_path.append([file_name, os.path.abspath(file_path)])
        else:
            mem_log = open(file_path, 'a+')
            mem_log.write(mem_line + '\n')
        mem_log.close()

    def write_cpu_info(self, cpu_detail: dict, package_name: str):
        """
        写入CPU使用情况
        :param cpu_detail:
        :param package_name:
        :return:
        """
        begin_line = 'timestamp,'
        cpu_line = ''
        for cpu_name, detail_info in cpu_detail.items():
            file_path = os.path.join(self.log_cpu_dir, 'cpu_{}_{}_log.txt'.format(cpu_name, package_name))
            if cpu_name == 'timestamp':
                cpu_line = str(detail_info) + ','
            if cpu_name == 'cpus':
                for core_name, cpu_data in detail_info.items():
                    # total = sum([float(i) for i in cpu_data.values()])
                    begin_line = begin_line + core_name.replace(' ', '') + ','
                    cpu_line = cpu_line + str(cpu_data['usage']) + ','
                if not os.path.exists(file_path):
                    cpu_log = open(file_path, 'a+')
                    cpu_log.write(begin_line + '\n')
                    cpu_log.write(cpu_line + '\n')
                else:
                    cpu_log = open(file_path, 'a+')
                    cpu_log.write(cpu_line + '\n')
                cpu_log.close()

    def generate_charts(self, log_dir: str, chart_type: str, title: str, decs: str, **kwargs):
        """
        通用的图表生成方法
        :param log_dir: 日志文件目录
        :param chart_type: 图表类型（用于文件名）
        :param title: 图表标题
        :param decs: 图表描述
        :param kwargs: 其他参数
        """
        file_list = [f for f in os.listdir(log_dir) if f.endswith('.txt')]
        for file_name in file_list:
            data_file_path = os.path.join(log_dir, file_name)
            output_title = file_name.replace('.txt', '')
            config = {
                'data_file': data_file_path,
                'title': title,
                'decs': decs,
                'output_file': os.path.join(self.log_view_dir, f"{chart_type}_{output_title}.html"),
                **kwargs
            }
            renderer = ChartRenderer(config)
            renderer.run()
