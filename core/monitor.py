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
        # flags = {
        #     "c": is_cpu,
        #     "r": is_memory,
        #     "f": is_fps,
        #     "net": is_net,
        #     "g": is_gpu,
        #     "t": is_temp,
        # }
        #
        # command = f"SP_daemon -PKG {package_name} -N 1"
        # for key, enabled in flags.items():
        #     if enabled:
        #         command += f" -{key}"
        #
        # logger.debug(f"SP_daemon command: {command}")
        # out = self.device.shell(command).output
        out = '''
          order:0 timestamp=1501839064260
          order:1 TotalcpuUsage=0.502513
          order:2 TotalcpuidleUsage=99.497487
          order:3 TotalcpuioWaitUsage=0.000000
          order:4 TotalcpuirqUsage=0.000000
          order:5 TotalcpuniceUsage=0.000000
          order:6 TotalcpusoftIrqUsage=0.000000
          order:7 TotalcpusystemUsage=0.251256
          order:8 TotalcpuuserUsage=0.251256
          order:9 cpu0Frequency=1992000
          order:10 cpu0Usage=1.000000
          order:11 cpu0idleUsage=99.000000
          order:12 cpu0ioWaitUsage=0.000000
          order:13 cpu0irqUsage=0.000000
          order:14 cpu0niceUsage=0.000000
          order:15 cpu0softIrqUsage=0.000000
          order:16 cpu0systemUsage=0.000000
          order:17 cpu0userUsage=1.000000
          order:18 cpu1Frequency=1992000
          order:19 cpu1Usage=0.000000
          order:20 cpu1idleUsage=100.000000
          order:21 cpu1ioWaitUsage=0.000000
          order:22 cpu1irqUsage=0.000000
          order:23 cpu1niceUsage=0.000000
          order:24 cpu1softIrqUsage=0.000000
          order:25 cpu1systemUsage=0.000000
          order:26 cpu1userUsage=0.000000
          order:27 cpu2Frequency=1992000
          order:28 cpu2Usage=1.000000
          order:29 cpu2idleUsage=99.000000
          order:30 cpu2ioWaitUsage=0.000000
          order:31 cpu2irqUsage=0.000000
          order:32 cpu2niceUsage=0.000000
          order:33 cpu2softIrqUsage=0.000000
          order:34 cpu2systemUsage=1.000000
          order:35 cpu2userUsage=0.000000
          order:36 cpu3Frequency=1992000
          order:37 cpu3Usage=0.000000
          order:38 cpu3idleUsage=100.000000
          order:39 cpu3ioWaitUsage=0.000000
          order:40 cpu3irqUsage=0.000000
          order:41 cpu3niceUsage=0.000000
          order:42 cpu3softIrqUsage=0.000000
          order:43 cpu3systemUsage=0.000000
          order:44 cpu3userUsage=0.000000
        '''
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

    @staticmethod
    def parser_cpu_data(cpu_data: Dict[str, Any]):
        """
        解析CPU数据
        :param cpu_data:
        :return:
        """
        freq_info = {}
        usage_info = {}
        for key, value in cpu_data.items():
            if re.match(r'cpu(\d+)Frequency', key):
                if value in (None, 'NA'):
                    freq_info[key] = 0
                else:
                    mhz_value = round(float(value) / 1_000_000, 2)  # MHz
                    freq_info[key] = mhz_value

            elif re.match(r'cpu(\d+)Usage', key):
                if value in (None, 'NA'):
                    usage_info[key] = 0
                else:
                    usage_info[key] = round(float(value), 2)

        return {"freq": freq_info, "usage": usage_info}

    @staticmethod
    def parser_memory_data(memory_data: Dict[str, Any]):
        """
        解析内存数据，输出格式：
        {
            "pss": 123.45,  # MB
            "NativePss": 12.34,
            ...
        }
        """
        memory_info = {}
        for key, value in memory_data.items():
            if (key.endswith("Pss") and not key.startswith("child")) or key == "pss":
                if value in (None, 'NA'):
                    memory_info[key] = 0
                else:
                    mb_value = float(value) / 1024
                    memory_info[key] = round(mb_value, 2)
        return memory_info

    @staticmethod
    def parser_fps_data(fps_data: Dict[str, Any]) -> Dict:
        """
        解析FPS数据，输出格式：
        {
            "fps": 60.0
        }
        """
        fps_info = {}
        value = fps_data.get("fps")
        if value not in (None, 'NA'):
            fps_info["fps"] = int(value)
        else:
            fps_info["fps"] = 0
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

        output_json = csv_file_path.replace(".csv", ".json")
        try:
            with open(output_json, 'w', encoding='utf-8') as f:
                import json
                json.dump(result, f, indent=2, default=default_serializer, ensure_ascii=False)
            logger.info(f"已保存到 {output_json}")
        except Exception as e:
            logger.error(f"写入JSON文件失败: {e}")


if __name__ == '__main__':
    monitor = Monitor("1")
    data = monitor.get_once_sp_daemon_data(package_name="com.tencent.mm")
    print(monitor.parser_cpu_data(cpu_data=data))
