# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/27 23:27
@Author   : wieszheng
@Software : PyCharm
"""
import os
from typing import Optional, Tuple
from loguru import logger
from hmdriver2.driver import Driver

from config.conf import ROOT_PATH
from utils.template_matching import find_image


class HDC:
    def __init__(self, serial: str = None):
        self.driver = self.init_hdc_driver(serial)
        self.is_share = ''

    def init_hdc_driver(self, serial=None) -> Optional[Driver]:
        """
        多设备
        :param serial:
        :return:
        """
        try:
            logger.debug("初始化HDC驱动...")
            return Driver(serial)
        except Exception as e:
            logger.error(e)
            return None

    def find_image(self, template_image: str, mode: str = 'template', share: bool = False, **kwargs) -> Optional[
        Tuple[int, int]]:
        """
        通过图像查找坐标
        :param template_image: 图像路径
        :param mode: 模式
        :param share: 是否共享
        :param kwargs: 传入参数
        :return:
        """
        source_image = os.path.join(ROOT_PATH, 'tmp', 'screenshot.jpeg')
        if share:
            self.is_share = source_image
        else:
            source_image = self.driver.screenshot(os.path.join(ROOT_PATH, 'tmp', 'screenshot.jpeg'))

        return find_image(source_image, template_image, method=mode, **kwargs)


if __name__ == '__main__':
    hdc = HDC()
    print(hdc.find_image(os.path.join(ROOT_PATH, r'config\pic\back.jpeg')))
