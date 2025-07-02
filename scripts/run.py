# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/29 16:22
@Author   : wieszheng
@Software : PyCharm
"""
import unittest

class Test(unittest.TestCase):
    def setUp(self):
        print("开始")

    def tearDown(self):
        print("结束")

    def test_01(self):
        print("test_01")

    def test_02(self):
        print("test_02")

if __name__ == '__main__':
    unittest.main()


