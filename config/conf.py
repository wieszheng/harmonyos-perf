# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 00:44
@Author   : wieszheng
@Software : PyCharm
"""
import os

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cpu_info = {

    "cpu0Frequency": {
        "data": [
            {
                "timestamp": "2025-06-28T11:22:54.174+0800",
                "value": 0.42,
            }
        ]
    },
    "cpu4Frequency": {1},
    "cpu10Frequency": {1},
    "cpuFreqIndex": {
        "data": [
            {
                "cpuFreqMax": 1.53,
                "cpuFreqMin": 0.42,
                "cpuFreqAve": 0.61,
                "coreName": "cpu0"
            }
        ]
    },


    "cpu0Usage": {
        "data": [
            {
                "timestamp": "2025-06-28T11:22:54.174+0800",
                "value": 33.98,
            }
        ]
    },
    "cpu1Usage": {1},
    "cpu2Usage": {1},
    "cpu3Usage": {1},
    "cpu4Usage": {1},
    "cpu5Usage": {1},
    "cpu6Usage": {1},
    "cpu7Usage": {1},
    "cpu8Usage": {1},
    "cpu9Usage": {1},
    "cpu10Usage": {1},
    "cpu11Usage": {1},
    "cpuCoreLoadIndex": {
        "data": [
            {
                "cpuCoreLoadMax": 78.79,
                "cpuCoreLoadMin": 15.09,
                "cpuCoreLoadAve": 33.53,
                "coreName": "cpu0"
            }
        ]
    },
}

mem_info = {
    "pss": {
        "data": [
            {
                "timestamp": "2025-06-28T11:22:54.174+0800",
                "value": 473.69,
            }
        ]
    },
    "arktsHeapPss": {},
    "gpuPss": {},
    "graphicPss": {},
    "nativeHeapPss": {},
    "stackPss": {},
    "swapPss": {},
    "memAppInfoIndex": {
        "data": [
            {
                "memInfoMax": 595.34,
                "memInfoMin": 399.17,
                "memInfoAve": 469.21,
                "coreName": "应用内存"
            },
            {
                "memInfoMax": 90.22,
                "memInfoMin": 66.7,
                "memInfoAve": 75.05,
                "coreName": "arkts内存"
            },
        ]
    },
}

gpu_info = {
    "gpuVisible": {1},
    "gpuFrequency": {1},
    "gpuFreqVisible": {1},
    "gpuLoad": {1},
    "gpuFreqIndex": {1},
    "gpuLoadIndex": {1},
}
fps_info = {
    "FPS": {
        "data": [
            {
                "timestamp": "2025-06-28T11:22:54.174+0800",
                "value": 0,
            }
        ]
    },
    "FPSIndex": {
        "data": [
            {
                "timestamp": "2025-06-28T11:27:53.858+0800",
                "value": 0,
                "tags": {
                    "FPSMax": 120,
                    "FPSMin": 1,
                    "FPSAve": 44.33,
                    "drop": 10,
                    "stutter": 0.19,
                    "littleJankSum": 7,
                    "mediumJankSum": 1,
                    "bigJankSum": 8
                }
            }
        ]
    },
}
