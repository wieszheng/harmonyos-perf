# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 18:54
@Author   : wieszheng
@Software : PyCharm
"""
import re
from datetime import datetime

import pandas as pd

df = pd.read_csv('t_index_info.csv', encoding='utf-8')

column_name = ['cpu0Frequency', 'cpu1Frequency', 'cpu2Frequency', 'cpu3Frequency', 'cpu4Frequency', 'cpu5Frequency',
               'cpu6Frequency', 'cpu7Frequency']

# 将该列的数据转换为JSON格式，每个值对应一个时间戳
timestamp_column = 'timestamp'
if timestamp_column not in df.columns:
    def convert_timestamp(ms):
        return datetime.fromtimestamp(ms / 1000).isoformat(timespec='milliseconds') + "+0800"


    df[timestamp_column] = df['timestamp'].apply(convert_timestamp)

result = {}
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

for col in numeric_columns:
    if col == 'timestamp':
        continue

    if col.startswith('cpu') and col.endswith('Frequency'):
        data = [
            {"timestamp": row[timestamp_column], "value": round(row[col] / 1_000_000, 2)}
            for _, row in df.iterrows()
        ]
        max_val = round(df[col].max() / 1_000_000, 2)
        min_val = round(df[col].min() / 1_000_000, 2)
        avg_val = round(df[col].mean() / 1_000_000, 2)
        result[col] = {"data": data}
        core_name = col.replace("Frequency", "")
        index_key = "cpuFreqIndex"

        result.setdefault(index_key, {"data": []})["data"].append({
            f"{index_key[:-5]}Max": max_val,
            f"{index_key[:-5]}Min": min_val,
            f"{index_key[:-5]}Ave": avg_val,
            "coreName": core_name
        })

    elif re.search(r'cpu(\d+)Usage', col):
        data = [
            {"timestamp": row[timestamp_column], "value": round(row[col], 2)}
            for _, row in df.iterrows()
        ]
        max_val = round(df[col].max(), 2)
        min_val = round(df[col].min(), 2)
        avg_val = round(df[col].mean(), 2)
        result[col] = {"data": data}
        core_name = col.replace("Usage", "")
        index_key = "cpuCoreLoadIndex"

        result.setdefault(index_key, {"data": []})["data"].append({
            f"{index_key[:-5]}Max": max_val,
            f"{index_key[:-5]}Min": min_val,
            f"{index_key[:-5]}Ave": avg_val,
            "coreName": core_name
        })
    elif (col.endswith("Pss") and not col.startswith("child")) or col == "pss":
        data = [
            {"timestamp": row[timestamp_column], "value": round(row[col] / 1024, 2)}
            for _, row in df.iterrows()
        ]
        max_val = round(df[col].max() / 1024, 2)
        min_val = round(df[col].min() / 1024, 2)
        avg_val = round(df[col].mean() / 1024, 2)
        result[col] = {"data": data}
        core_name = col
        index_key = "memAppInfoIndex"

        result.setdefault(index_key, {"data": []})["data"].append({
            f"memInfoMax": max_val,
            f"memInfoMin": min_val,
            f"memInfoAve": avg_val,
            "coreName": core_name
        })


output_json = 'converted_data.json'
with open(output_json, 'w') as f:
    import json

    json.dump(result, f, indent=4)

print(f"已保存到 {output_json}")
