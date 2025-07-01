# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/30 22:23
@Author   : wieszheng
@Software : PyCharm
"""
import os
import re
from datetime import datetime
from typing import Any, Dict

import pandas as pd
from loguru import logger

from hmdriver2.driver import Driver
from pandas import Timestamp


class Monitor:
    def __init__(self, hdc: Any):
        pass
        # self.device: Driver = hdc.device

    def get_once_sp_daemon_data(
            self,
            package_name: str,
            is_cpu: bool = True,
            is_memory: bool = True,
            is_fps: bool = True,
            is_net: bool = False,
            is_gpu: bool = False,
            is_temp: bool = False,
    ) -> Dict[str, Any]:
        """
        获取一次SP_daemon数据
        :param package_name:
        :param is_cpu:
        :param is_memory:
        :param is_fps:
        :param is_net:
        :param is_gpu:
        :param is_temp:
        :return:
        """
        flags = {
            "c": is_cpu,
            "r": is_memory,
            "f": is_fps,
            "net": is_net,
            "g": is_gpu,
            "t": is_temp,
        }

        command = f"SP_daemon -PKG {package_name} -N 1"
        for key, enabled in flags.items():
            if enabled:
                command += f" -{key}"

        logger.debug(f"SP_daemon command: {command}")
        out = self.device.shell(command).output
        data_block = re.search(r'(?s)order:.*', out)
        if not data_block:
            logger.error("内存数据格式不正确，未找到有效数据块")
            raise ValueError("内存数据格式不正确，未找到有效数据块")
        raw_data = data_block.group(0)
        parsed_data = {}

        for line in raw_data.strip().split('\n'):
            line = line.strip()
            if not line or '=' not in line:
                continue

            try:
                match = re.search(r'(\w+)=(NA|\d+\.?\d*|\w[\w\.\-]*)', line)
                if match:
                    key, value = match.groups()
                    parsed_data[key] = None if value == 'NA' else value
            except Exception as e:
                logger.error(f"解析数据错误：{e}")
                raise ValueError(f"解析数据错误：{e}")

        return parsed_data

    def write_once_sp_daemon_csv(
            self,
            data: Dict[str, Any],
            filename: str,
    ):
        """
        写入SP_daemon数据
        :param data:
        :param filename:
        :return:
        """
        file_exists = os.path.isfile(filename)
        df = pd.DataFrame([data])
        df.to_csv(filename, mode='a', header=not file_exists, index=False)

    def parser_cpu_data(self, cpu_data: Dict[str, Any]):
        """
        解析CPU数据
        :param cpu_data:
        :return:
        """
        cpu_info = {}
        for key, value in cpu_data.items():
            if re.search(r'cpu(\d+)Frequency', key):
                mhz_value = round(float(value) / 1_000_000, 2)  # MHz
                cpu_info[key] = mhz_value
            elif re.search(r'cpu(\d+)Usage', key):
                cpu_info[key] = round(float(value), 2)

        return cpu_info

    def parser_memory_data(self, memory_data: Dict[str, Any]):
        """
        解析内存数据
        :param memory_data:
        :return:
        """
        memory_info = {}
        for key, value in memory_data.items():
            if (key.endswith("Pss") and not key.startswith("child")) or key == "pss":
                mb_value = round(float(value) / 1024, 2)  # MB
                memory_info[key] = mb_value
        return memory_info

    def parser_fps_data(self, fps_data: Dict[str, Any]):
        """
        解析FPS数据
        :param fps_data:
        :return:
        """
        fps_info = {}
        for key, value in fps_data.items():
            if key == "fps":
                fps_info[key] = value
        return fps_info

    def parser_net_data(self):
        pass

    def parser_gpu_data(self):
        pass

    def parser_temp_data(self):
        pass

    def parser_data_to_json(self, csv_file_path: str):
        """
        解析CSV文件，生成结构化JSON数据并保存
        :param csv_file_path: 输入CSV路径
        :param output_json: 输出JSON路径
        """
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
        except Exception as e:
            logger.error(f"读取CSV文件失败: {e}")
            return

        result = {}
        cpu_freq_stats, cpu_usage_stats, mem_stats = [], [], []

        def build_series(col, func, scale=1):
            return [
                {"timestamp": row['timestamp'], "value": round(func(row[col]), 2)}
                for _, row in df.iterrows()
            ]

        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        for col in numeric_columns:
            if col == "timestamp":
                continue

            if re.search(r'cpu(\d+)Frequency', col):
                core_name = col.replace('Frequency', '')
                freq_series = df[col] / 1_000_000
                result[col] = {"data": build_series(col, lambda x: x / 1_000_000)}
                cpu_freq_stats.append({
                    "Max": round(freq_series.max(), 2),
                    "Min": round(freq_series.min(), 2),
                    "Ave": round(freq_series.mean(), 2),
                    "Name": core_name
                })
            elif re.search(r'cpu(\d+)Usage', col):
                core_name = col.replace("Usage", "")
                result[col] = {"data": build_series(col, float)}
                cpu_usage_stats.append({
                    "Max": round(df[col].max(), 2),
                    "Min": round(df[col].min(), 2),
                    "Ave": round(df[col].mean(), 2),
                    "Name": core_name
                })
            elif (col.endswith("Pss") and not col.startswith("child")) or col == "pss":
                result[col] = {"data": build_series(col, lambda x: x / 1024)}
                mem_stats.append({
                    "Max": round(df[col].max() / 1024, 2),
                    "Min": round(df[col].min() / 1024, 2),
                    "Ave": round(df[col].mean() / 1024, 2),
                    "Name": col
                })

        result["cpuFreqIndex"] = {"data": cpu_freq_stats}
        result["cpuCoreLoadIndex"] = {"data": cpu_usage_stats}
        result["memAppInfoIndex"] = {"data": mem_stats}

        def default_serializer(obj):
            if isinstance(obj, Timestamp):
                return obj.isoformat()
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        try:
            with open(output_json, 'w', encoding='utf-8') as f:
                import json
                json.dump(result, f, indent=2, default=default_serializer, ensure_ascii=False)
            logger.info(f"已保存到 {output_json}")
        except Exception as e:
            logger.error(f"写入JSON文件失败: {e}")
if __name__ == '__main__':
    monitor = Monitor("1")
    monitor.parser_data_to_json("../utils/t_index_info.csv")

