# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/28 00:55
@Author   : wieszheng
@Software : PyCharm
"""
import re
from datetime import datetime
from typing import List, Dict, Any

from loguru import logger

from core.hdc import HDC
from hmdriver2.driver import Driver


class CpuMonitor:
    def __init__(self, device):
        self.device: Driver = device

    def get_pid(self, package_name: str) -> List[str]:
        """
        获取进程pid
        :param package_name:
        :return:
        """
        out = self.device.shell("ps -f | grep %s" % package_name).output
        pid = []
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("shell"):
                continue
            elif package_name in line:
                line_data = line.split()
                pid.append(line_data[1])
        return pid

    def get_cpu_usage(self, pid: str) -> Dict[str, Any]:
        """
        获取进程cpu使用率
        :param pid:
        :return:
        """
        cpu_data = ["PID", "Total Usage", "User Space", "Kernel Space", "Page Fault Minor", "Page Fault Major", "Name"]
        cpu_list_data = []
        out = self.device.shell("hidumper --cpuusage %s" % pid).output
        for line in out.splitlines():
            line = line.strip()

            if line.startswith("PID"):
                continue
            elif line.startswith(str(pid)):
                line_data = line.split()
                for i in line_data:
                    if i != " ":
                        cpu_list_data.append(i)

        if len(cpu_list_data) != len(cpu_data):
            # raise
            print("Invalid CPU data")
        return dict(zip(cpu_data, cpu_list_data))

    def get_sp_daemon_cpu(self, package_name: str) -> Dict[str, Any]:
        """
        获取sp_daemon进程cpu使用率
        :param package_name:
        :return:
        """
        out = self.device.shell(f"SP_daemon -PKG {package_name} -c -N 1").output
        data_block = re.search(r'(?s)order:.*', out)
        if not data_block:
            raise ValueError("内存数据格式不正确，未找到有效数据块")
        raw_data = data_block.group(0)
        # 准备数据结构
        result: Dict[str, Any] = {
            "timestamp": 0,
            "process": {},
            "system": {},
            "cpus": {}
        }

        for line in raw_data.split("\n"):
            line = line.strip()
            if not line or "=" not in line:
                continue

            try:
                # 提取键值对
                if line.startswith("order:"):
                    # 处理"order:X key=value"格式
                    parts = re.split(r"\s+", line, 1)
                    key_value = parts[1] if len(parts) > 1 else ""

                    if "=" in key_value:
                        key, value = key_value.split("=", 1)
                        self.process_key_value(result, key, value)
                else:
                    # 直接处理"key=value"格式
                    key, value = line.split("=", 1)
                    self.process_key_value(result, key, value)

            except (IndexError, ValueError) as e:
                logger.warning(f"解析行失败: {line} - {str(e)}")
                continue

        return result
    def process_key_value(self, result: Dict[str, Any], key: str, value: str):
        """
        处理键值对
        :param result:
        :param key:
        :param value:
        :return:
        """
        if value == "NA":
            value = None
        else:
            try:
                value = float(value) if "." in value else int(value)
            except ValueError:
                pass

        if key == "timestamp":
            result["timestamp"] = value

        # 进程相关信息
        elif key in ["ProcAppName", "ProcId", "ProcCpuLoad", "ProcCpuUsage", "ProcSCpuUsage", "ProcUCpuUsage"]:
            result["process"][key] = value

        # 子进程信息(当前都为NA)
        elif key.startswith("ChildProc"):
            if "child_processes" not in result:
                result["child_processes"] = {}
            result["child_processes"][key] = value

        # 系统级CPU指标
        elif key.startswith("Totalcpu"):
            result["system"][key] = value

        # CPU核心指标
        elif key.startswith("cpu") and any(char.isdigit() for char in key):
            self.handle_cpu_core_metric(result, key, value)

    def handle_cpu_core_metric(self, result: Dict[str, Any], key: str, value: Any):
        """
        处理CPU核心指标
        :param result:
        :param key:
        :param value:
        :return:
        """
        # 匹配核心编号和指标类型
        match = re.match(r"^(cpu\d+)(\w+)$", key)
        if not match:
            return

        core_name = match.group(1)
        metric_name = match.group(2)
        # 确保核心对象存在
        if core_name not in result["cpus"]:
            result["cpus"][core_name] = {
                "frequency": 0,
                "usage": 0.0,
                "idle": 0.0,
                "system": 0.0,
                "user": 0.0,
                "irq": 0.0,
            }

        # 根据指标类型赋值
        if metric_name == "Frequency":
            result["cpus"][core_name]["frequency"] = value
        elif metric_name == "Usage":
            result["cpus"][core_name]["usage"] = value
        elif metric_name == "idleUsage":
            result["cpus"][core_name]["idle"] = value
        elif metric_name == "systemUsage":
            result["cpus"][core_name]["system"] = value
        elif metric_name == "userUsage":
            result["cpus"][core_name]["user"] = value
        elif metric_name == "irqUsage":
            result["cpus"][core_name]["irq"] = value
        else:
            result["cpus"][core_name][metric_name.lower()] = value

if __name__ == '__main__':
    hdc = HDC()
    cpu = CpuMonitor(hdc.driver)

    print(cpu.get_sp_daemon_cpu("com.baidu.yiyan.ent"))
