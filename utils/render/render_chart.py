# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 00:48
@Author   : wieszheng
@Software : PyCharm
"""
import jinja2
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from loguru import logger

from config.conf import ROOT_PATH


class ChartRenderer:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化图表渲染器
        :param config:
        """
        self.config = config
        self.data_file = config.get('data_file', 'data.txt')
        self.time_col = config.get('time_col', 'timestamp')
        self.time_format = config.get('time_format', '%H:%M:%S')
        self.output_file = config.get('output_file', 'chart.html')
        self.template_file = config.get('template_file', '../template.html')
        self.unit = config.get('unit', '%')
        self.title = config.get('title', '未知')
        self.decs = config.get('decs', '未知')

        self.headers: List[str] = []
        self.data_rows: List[List[str]] = []
        self.x_labels: List[str] = []
        self.series: List[Dict[str, Any]] = []
        self.table_data: List[Dict[str, Any]] = []

        self.legend_map = {
            'total_pss_mb': '应用内存',
            'native_heap_pss_mb': 'native内存',
            'ark_ts_heap_pss_mb': 'arkts内存',
            'gpu_pss_mb': 'gpu内存',
            'graphic_pss_mb': '图形内存',
            'stack_pas_mb': '栈内存',
            'swap_pss_mb': '交换内存',
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

    def load_data(self) -> bool:
        """
        加载数据
        :return:
        """
        if not os.path.exists(self.data_file):
            logger.warning(f"❌ 数据文件不存在: {self.data_file}")
            return False

        with open(self.data_file, encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 2:
            logger.warning(f"❌ 数据文件格式错误: 至少需要表头和数据行")
            return False

        # 解析表头和数据和过滤空列
        self.headers = lines[0].split(',')
        self.data_rows = [line.split(',') for line in lines[1:]]
        self.headers = [h for h in self.headers if h.strip()]
        self.data_rows = [[cell for cell in row if cell.strip()] for row in self.data_rows]

        logger.success(f"✅ 成功加载数据: {len(self.headers)}列, {len(self.data_rows)}行")
        return True

    def parse_time(self, ts: str) -> str:
        """
        解析时间戳为格式化时间
        :param ts:
        :return:
        """
        try:
            timestamp = int(ts)
            if timestamp > 1e10:  # 毫秒时间戳
                timestamp = timestamp // 1000
            return datetime.fromtimestamp(timestamp).strftime(self.time_format)
        except (ValueError, OSError):
            return ts

    def process_data(self) -> bool:
        """
        处理数据，生成图表所需的数据结构
        :return:
        """
        try:
            if self.time_col not in self.headers:
                logger.warning(f"❌ 未找到时间列: {self.time_col}")
                return False

            time_idx = self.headers.index(self.time_col)
            data_indices = [i for i in range(len(self.headers)) if i != time_idx]
            data_headers = [self.headers[i] for i in data_indices]

            # 生成横坐标（时间）
            self.x_labels = [self.parse_time(row[time_idx]) for row in self.data_rows]

            # 生成系列数据
            self.series = []
            self.table_data = []

            for i, col in zip(data_indices, data_headers):
                values = []
                legend_name = self.legend_map.get(col, col)  # 优先用映射，否则用原名
                for row in self.data_rows:
                    try:
                        v = float(row[i])
                        values.append(v)
                    except (ValueError, IndexError):
                        values.append(0)

                if not values:
                    continue

                # 计算统计值
                avg = round(sum(values) / len(values), 1)
                vmax = round(max(values), 1)
                vmin = round(min(values), 1)

                # 添加到系列
                self.series.append({
                    'name': legend_name,
                    'type': 'line',
                    'data': values
                })

                # 添加到表格数据
                self.table_data.append({
                    'name': legend_name,
                    'avg': avg,
                    'max': vmax,
                    'min': vmin
                })

            logger.success(f"✅ 成功处理数据: {len(self.series)}个系列")
            return True

        except Exception as e:
            logger.error(f"❌ 处理数据失败: {e}")
            return False

    def render_template(self) -> bool:
        """
        渲染模板
        :return:
        """
        path = os.path.join(ROOT_PATH, "config", "template")
        if not os.path.exists(path):
            logger.warning(f"❌ 模板文件不存在: {path}")
            return False

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
        template = env.get_template(self.template_file)

        html = template.render(
            x_labels=json.dumps(self.x_labels),
            series=json.dumps(self.series),
            table_data=self.table_data,
            unit='"{}"'.format(self.unit),
            title=self.title,
            decs=self.decs
        )

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.success(f"✅ 成功生成图表: {self.output_file}")
        return True

    def run(self) -> bool:
        """运行完整的渲染流程"""
        logger.debug("🚀 开始渲染图表...")
        logger.debug(f"📁 数据文件: {self.data_file}")
        logger.debug(f"📁 模板文件: {self.template_file}")
        logger.debug(f"📁 输出文件: {self.output_file}")
        logger.debug("-" * 50)

        if not self.load_data():
            return False

        if not self.process_data():
            return False

        if not self.render_template():
            return False

        logger.debug("-" * 50)
        logger.debug("🎉 图表渲染完成！")
        logger.debug(f"📊 数据系列: {len(self.series)}个")
        logger.debug(f"📈 数据点: {len(self.x_labels)}个")
        logger.debug(f"📋 表格行: {len(self.table_data)}行")
        if self.unit:
            logger.debug(f"📏 单位: {self.unit}")

        return True
