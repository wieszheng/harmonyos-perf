# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 16:22
@Author   : wieszheng
@Software : PyCharm
"""
import argparse
from wxy_dialogue import Dialogue

def main():
    parser = argparse.ArgumentParser(description='HarmonyOS性能测试工具')
    parser.add_argument('--device', type=str, required=True, help='设备ID')
    parser.add_argument('--package', type=str, required=True, help='应用包名')
    parser.add_argument('--activity', type=str, help='主Activity')
    args = parser.parse_args()



if __name__ == "__main__":
    main()