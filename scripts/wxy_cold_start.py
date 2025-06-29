# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/27 23:25
@Author   : wieszheng
@Software : PyCharm
"""
import time

from hmdriver2.driver import Driver

from core.executor import Executor
from core.hdc import HDC


class ColdStart(Executor):
    """
    冷启动
    """

    def __init__(self, hdc: Driver, name: str = ""):
        super().__init__(name)
        self.hdc = hdc

    def set_up(self) -> None:
        self._log("清理文小言进行冷启动")
        self.hdc.stop_app("com.baidu.yiyan.ent")
        self.hdc.go_home()
        time.sleep(2)
    def execute(self):
        self._log("执行中...")
        self.hdc.start_app("com.baidu.yiyan.ent")
        time.sleep(10)
    def set_down(self) -> None:
        pass


if __name__ == '__main__':
    # 测试示例
    hdc = HDC()
    executor = ColdStart(hdc.driver, "文小言冷启动")
    for i in range(10):
        executor.run()
