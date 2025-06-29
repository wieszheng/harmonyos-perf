# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/27 23:26
@Author   : wieszheng
@Software : PyCharm
"""
import os
import time

from hmdriver2.driver import Driver

from config.conf import ROOT_PATH
from core.executor import Executor
from core.hdc import HDC

questions = [
    # "如何实现对多个 PID 的批量内存采集与趋势分析？",
    # "请解释虚拟DOM的核心原理，它相比直接操作真实DOM的优势是什么？实际开发中，哪些场景下虚拟DOM的性能反而不如直接操作真实DOM",
    # "在微服务架构下，如何解决跨服务的事务一致性问题？请对比2PC（两阶段提交）、TCC（补偿事务）、Saga模式的适用场景和优缺点",
    # "假设你负责一个电商商品详情页的开发，前端需要展示商品价格、库存、推荐列表等信息。请描述你会如何设计与后端的接口（包括URL、Method、参数、返回格式），并说明联调过程中可能遇到的问题及解决思路",
    # "一个H5页面首屏加载时间过长（3s+），请从资源加载、渲染优化、代码层面给出具体的优化方案，并说明如何量化优化效果",
    # "为什么需要状态管理库？以Redux为例，说明其核心概念（Store、Action、Reducer）的作用，以及中间件（如Redux Thunk）解决了什么问题",
    "缓存是提升系统性能的关键，但可能引发缓存穿透（查询不存在的数据）、击穿（热点Key失效）、雪崩（大量Key同时失效）。请分别说明这三个问题的原因，并给出对应的解决方案（如布隆过滤器、互斥锁、随机过期时间）",
]


class Dialogue(Executor):
    """
    对话
    """

    def __init__(self, hdc: HDC, name: str = ""):
        super().__init__(name)
        self.hdc = hdc
        self.device: Driver = hdc.driver
        self.model_name = 'r1_model'

    def set_up(self):
        self._log("清理文小言进行冷启动")
        self.device.stop_app("com.baidu.yiyan.ent")
        self.device.go_home()
        time.sleep(2)

    def set_model_name(self, model_name: str):
        self.model_name = model_name

    def model_switch(self, model_name: str):

        self._log(f"切换模型 {model_name}")
        models = {
            'r1_model': '//root[1]/Popup[1]/Column[1]/Column[1]/Scroll[1]/Flex[1]/Row[3]/Column[1]',
            'wx_model': '//root[1]/Popup[1]/Column[1]/Column[1]/Scroll[1]/Flex[1]/Row[2]/Column[1]',
            'auto_model': '//root[1]/Popup[1]/Column[1]/Column[1]/Scroll[1]/Flex[1]/Row[1]/Column[1]'
        }
        if models.get(model_name):
            self.device.xpath(models[model_name]).click()
        else:
            self._log(f"未找到模型 {model_name}")

    def execute(self):
        self._log("启动应用.")
        self.device.start_app("com.baidu.yiyan.ent")
        time.sleep(2)

        self.device.xpath('//*[@text="文小言"]').click()
        self.model_switch(self.model_name)

        for question in questions:
            self._log(f"对话: {question}")
            self.device.xpath(
                '//root[1]/Column[1]/__Common__[1]/SideBarContainer[1]/Stack[1]/Column[1]/__Common__[1]/Tabs[1]/Swiper[1]'
                '/TabContent[1]/Column[1]/__Common__[2]/Column[1]/__Common__[1]/Column[1]/Stack[1]/Column[1]/Flex[1]/Row[1]'
                '/Scroll[1]').input_text(question)
            self._log("发送")
            self.device.xpath('//root[1]/Column[1]/__Common__[1]/SideBarContainer[1]/Stack[1]/Column[1]/__Common__[1]'
                              '/Tabs[1]/Swiper[1]/TabContent[1]/Column[1]/__Common__[2]/Column[1]/__Common__[1]/Column[1]'
                              '/Stack[1]/Column[1]/Flex[1]/Row[2]/Row[1]/Stack[1]').click()
            while True:
                time.sleep(1)
                if not self.hdc.find_image(os.path.join(ROOT_PATH, 'config', 'pic', 'ans.jpeg')):
                    break

                result = self.hdc.find_image(os.path.join(ROOT_PATH, 'config', 'pic', 'back.jpeg'), share=True,
                                             mode='sift')
                if result:
                    x, y = result
                    self.device.double_click(x, y)

    def set_down(self) -> None:
        pass


if __name__ == '__main__':
    hdc = HDC()
    executor = Dialogue(hdc, "文小言对话")
    executor.run()
