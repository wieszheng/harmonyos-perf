#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON数据多图表渲染脚本
支持CPU频率、CPU使用率、内存使用等多个维度的数据可视化
"""

import jinja2
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

class JsonChartRenderer:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化JSON图表渲染器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.json_file = config.get('json_file', 'converted_data.json')
        self.output_file = config.get('output_file', 'dashboard.html')
        self.template_file = config.get('template_file', '../template.html')

        # 数据存储
        self.data: Dict[str, Any] = {}
        self.legend_map = {
            'pss': '应用内存',
            'nativeHeapPss': 'native内存',
            'arktsHeapPss': 'arkts内存',
            'gpuPss': 'gpu内存',
            'graphicPss': '图形内存',
            'stackPss': '栈内存',
            'swapPss': '交换内存',
            'cpu0': 'CPU0',
            'cpu1': 'CPU1',
            'cpu2': 'CPU2',
            'cpu3': 'CPU3',
            'cpu4': 'CPU4',
            'cpu5': 'CPU5',
            'cpu6': 'CPU6',
            'cpu7': 'CPU7',
            'cpu8': 'CPU8',
            'cpu9': 'CPU9',
            'cpu10': 'CPU10',
            'cpu11': 'CPU11',
            'cpu12': 'CPU12',
            'cpu13': 'CPU13',
            'cpu14': 'CPU14',
            'cpu15': 'CPU15',
        }

    def load_json_data(self) -> bool:
        """加载JSON数据文件"""
        try:
            if not os.path.exists(self.json_file):
                print(f"❌ JSON文件不存在: {self.json_file}")
                return False

            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            print(f"✅ 成功加载JSON数据: {len(self.data)}个数据组")
            return True

        except Exception as e:
            print(f"❌ 加载JSON数据失败: {e}")
            return False

    def parse_time(self, ts: int) -> str:
        """解析时间戳为格式化时间"""
        try:
            if ts > 1e10:  # 毫秒时间戳
                ts = ts // 1000
            return datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        except (ValueError, OSError):
            return str(ts)

    def process_cpu_frequency_data(self) -> tuple:
        """处理CPU频率数据"""
        cpu_freq_series = []
        cpu_freq_timestamps = []
        cpu_freq_stats = []

        # 获取统计信息
        if 'cpuFreqIndex' in self.data:
            cpu_freq_stats = self.data['cpuFreqIndex']['data']
            for item in cpu_freq_stats:
                item['coreName'] = self.legend_map[item['coreName']]

        # 获取时序数据
        for i in range(12):  # cpu0-cpu11
            key = f'cpu{i}Frequency'
            if key in self.data:
                series_data = self.data[key]['data']

                # 提取时间戳和数值
                timestamps = [self.parse_time(item['timestamp']) for item in series_data]
                values = [item['value'] for item in series_data]

                # 设置时间戳（只设置一次）
                if not cpu_freq_timestamps:
                    cpu_freq_timestamps = timestamps

                # 添加到系列
                cpu_freq_series.append({
                    'name': f'CPU {i}',
                    'type': 'line',
                    'data': values
                })

        return cpu_freq_series, cpu_freq_timestamps, cpu_freq_stats

    def process_cpu_usage_data(self) -> tuple:
        """处理CPU使用率数据"""
        cpu_usage_series = []
        cpu_usage_timestamps = []
        cpu_usage_stats = []

        # 获取统计信息
        if 'cpuCoreLoadIndex' in self.data:
            cpu_usage_stats = self.data['cpuCoreLoadIndex']['data']
            for item in cpu_usage_stats:
                item['coreName'] = self.legend_map[item['coreName']]

        # 获取时序数据
        for i in range(12):  # cpu0-cpu11
            key = f'cpu{i}Usage'
            if key in self.data:
                series_data = self.data[key]['data']

                # 提取时间戳和数值
                timestamps = [self.parse_time(item['timestamp']) for item in series_data]
                values = [item['value'] for item in series_data]

                # 设置时间戳（只设置一次）
                if not cpu_usage_timestamps:
                    cpu_usage_timestamps = timestamps

                # 添加到系列
                cpu_usage_series.append({
                    'name': f'CPU {i}',
                    'type': 'line',
                    'data': values
                })

        return cpu_usage_series, cpu_usage_timestamps, cpu_usage_stats

    def process_memory_data(self) -> tuple:
        """处理内存使用数据"""
        memory_series = []
        memory_timestamps = []
        memory_stats = []

        # 获取统计信息
        if 'memAppInfoIndex' in self.data:
            memory_stats = self.data['memAppInfoIndex']['data']
            for item in memory_stats:
                item['coreName'] = self.legend_map[item['coreName']]


        # 内存相关的键
        memory_keys = ['arktsHeapPss', 'gpuPss', 'graphicPss', 'nativeHeapPss', 'pss', 'stackPss', 'swapPss']

        # 获取时序数据
        for key in memory_keys:
            if key in self.data:
                series_data = self.data[key]['data']

                # 提取时间戳和数值
                timestamps = [self.parse_time(item['timestamp']) for item in series_data]
                values = [item['value'] for item in series_data]

                # 设置时间戳（只设置一次）
                if not memory_timestamps:
                    memory_timestamps = timestamps

                # 添加到系列
                memory_series.append({
                    'name': self.legend_map[key],
                    'type': 'line',
                    'data': values
                })

        return memory_series, memory_timestamps, memory_stats

    def render_template(self) -> bool:
        """渲染模板"""
        try:
            if not os.path.exists(self.template_file):
                print(f"❌ 模板文件不存在: {self.template_file}")
                return False

            # 处理各类数据
            cpu_freq_series, cpu_freq_timestamps, cpu_freq_stats = self.process_cpu_frequency_data()
            cpu_usage_series, cpu_usage_timestamps, cpu_usage_stats = self.process_cpu_usage_data()
            memory_series, memory_timestamps, memory_stats = self.process_memory_data()

            print(f"✅ CPU频率数据: {len(cpu_freq_series)}个系列")
            print(f"✅ CPU使用率数据: {len(cpu_usage_series)}个系列")
            print(f"✅ 内存数据: {len(memory_series)}个系列")

            # 创建Jinja2环境
            env = jinja2.Environment(loader=jinja2.FileSystemLoader('..'))
            template = env.get_template(self.template_file)

            # 渲染模板
            html = template.render(
                cpu_freq_series=json.dumps(cpu_freq_series),
                cpu_freq_timestamps=json.dumps(cpu_freq_timestamps),
                cpu_freq_stats=cpu_freq_stats,
                cpu_usage_series=json.dumps(cpu_usage_series),
                cpu_usage_timestamps=json.dumps(cpu_usage_timestamps),
                cpu_usage_stats=cpu_usage_stats,
                memory_series=json.dumps(memory_series),
                memory_timestamps=json.dumps(memory_timestamps),
                memory_stats=memory_stats
            )

            # 写入文件
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"✅ 成功生成仪表板: {self.output_file}")
            return True

        except Exception as e:
            print(f"❌ 渲染模板失败: {e}")
            return False

    def run(self) -> bool:
        """运行完整的渲染流程"""
        print("🚀 开始渲染JSON数据仪表板...")
        print(f"📁 JSON文件: {self.json_file}")
        print(f"📁 模板文件: {self.template_file}")
        print(f"📁 输出文件: {self.output_file}")
        print("-" * 50)

        if not self.load_json_data():
            return False

        if not self.render_template():
            return False

        print("-" * 50)
        print("🎉 JSON数据仪表板渲染完成！")

        return True


def main():
    """主函数"""
    # 默认配置
    config = {
        'json_file': 'converted_data.json',
        'output_file': 'dashboard.html',
        'template_file': 'template.html'
    }

    # 创建渲染器并运行
    renderer = JsonChartRenderer(config)
    success = renderer.run()

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()