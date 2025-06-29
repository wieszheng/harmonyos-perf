# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/28 00:55
@Author   : wieszheng
@Software : PyCharm
"""
import re
from typing import Dict, Any

from loguru import logger

from core.hdc import HDC
from hmdriver2.driver import Driver


def find_first_digit(data):
    """
    从字符串中找出第一个数字
    :param data:
    :return:
    """
    for index, item in enumerate(data):
        if item.isdigit():  # 只能判断非负整数字符串
            return {
                "index": index,
                "value": int(item),
                "type": "int"
            }
    return None


class MemoryMonitor:
    def __init__(self, device):
        self.device: Driver = device

    def get_hidumper_memory(self, pid: str) -> Dict[str, Any]:
        """
        获取指定进程的内存信息
        :param pid:
        :return:
        """
        mem_data = {
            "GL": 0,
            "Graph": 0,
            "ark ts heap": 0,
            "guard": 0,
            "native heap": 0,
            "AnonPage other": 0,
            "stack": 0,
            "dev": 0,
            "FilePage other": 0
        }

        # 使用hidumper --mem获取系统内存信息
        out = self.device.shell(f"hidumper --mem {pid}").output

        for line in out.splitlines():
            line = line.strip()
            if line.startswith("GL"):
                mem_data["GL"] = find_first_digit(line.split()).get("value")
            elif line.startswith("Graph"):
                mem_data["Graph"] = find_first_digit(line.split()).get("value")
            elif line.startswith("ark"):
                mem_data["ark ts heap"] = find_first_digit(line.split()).get("value")
            elif line.startswith("guard"):
                mem_data["guard"] = find_first_digit(line.split()).get("value")
            elif line.startswith("native"):
                mem_data["native heap"] = find_first_digit(line.split()).get("value")
            elif line.startswith("AnonPage"):
                mem_data["AnonPage other"] = find_first_digit(line.split()).get("value")
            elif line.startswith("stack"):
                mem_data["stack"] = find_first_digit(line.split()).get("value")
            elif line.startswith("dev"):
                mem_data["dev"] = find_first_digit(line.split()).get("value")
            elif line.startswith("FilePage"):
                mem_data["FilePage other"] = find_first_digit(line.split()).get("value")
                break
        mem_data["Total"] = sum(value for value in mem_data.values() if isinstance(value, int))
        return mem_data

    def get_sp_daemon_memory(self, package_name: str) -> Dict[str, Any]:
        """
        获取指定包名的进程的内存信息
        :param package_name:
        :return:
        """
        out = self.device.shell(f"SP_daemon -PKG {package_name} -r -N 1").output
        data_block = re.search(r'(?s)order:.*', out)
        if not data_block:
            raise ValueError("内存数据格式不正确，未找到有效数据块")
        raw_data = data_block.group(0)
        parsed_data = {}
        for line in raw_data.strip().split('\n'):
            line = line.strip()
            if not line or '=' not in line:
                continue
            # 提取键和值
            try:
                # 处理 "order:X key=value" 格式
                parts = re.split(r'\s+', line, 1)
                key_value = parts[-1]
                if '=' in key_value:
                    key, value = key_value.split('=', 1)
                    if value == 'NA':
                        parsed_data[key] = None
                    else:
                        try:
                            parsed_data[key] = int(value)
                        except ValueError:
                            try:
                                parsed_data[key] = float(value)
                            except ValueError:
                                parsed_data[key] = value  # 保留为字符串
            except (IndexError, ValueError) as e:
                logger.warning(f"解析行失败: {line} - {str(e)}")
                continue
        return {
            'total_pss_mb': round(parsed_data.get('pss', 0) / 1024, 2) if parsed_data.get('pss') else 0,
            'native_heap_pss_mb': round(parsed_data.get('nativeHeapPss', 0) / 1024, 2) if parsed_data.get(
                'nativeHeapPss') else 0,
            'ark_ts_heap_pss_mb': round(parsed_data.get('arktsHeapPss', 0) / 1024, 2) if parsed_data.get(
                'arktsHeapPss') else 0,
            'gpu_pss_mb': round(parsed_data.get('gpuPss', 0) / 1024, 2) if parsed_data.get('gpuPss') else 0,
            'graphic_pss_mb': round(parsed_data.get('graphicPss', 0) / 1024, 2) if parsed_data.get('graphicPss') else 0,
            'stack_pas_mb': round(parsed_data.get('stackPss', 0) / 1024, 2) if parsed_data.get('stackPss') else 0,
            'swap_pss_mb': round(parsed_data.get('swapPss', 0) / 1024, 2) if parsed_data.get('swapPss') else 0,
            'timestamp': parsed_data.get('timestamp', 0),
        }


if __name__ == '__main__':
    # 测试示例
    hdc = HDC()
    if hdc.driver:
        memory_monitor = MemoryMonitor(hdc.driver)

        print(memory_monitor.get_sp_daemon_memory("com.baidu.yiyan.ent"))
    else:
        print("HDC驱动初始化失败")
