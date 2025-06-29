#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/28 00:55
@Author   : wieszheng
@Software : PyCharm
"""
import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from datetime import datetime

from loguru import logger


class Executor(ABC):
    """
    基础执行器类
    提供统一的执行流程：set_up -> execute -> set_down
    子类需要实现具体的set_up、execute、set_down方法
    """

    def __init__(self, name: str = None, config: Dict[str, Any] = None):
        """
        初始化执行器
        :param name:
        :param config:
        """
        self.name = name or self.__class__.__name__
        self.config = config or {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.is_setup = False
        self.is_executed = False
        self.is_teardown = False

    def run(self) -> Any:
        """
        执行完整的执行流程：set_up -> execute -> set_down
        :return:
        """
        try:
            # 1. 初始化阶段
            self._log("开始初始化...")
            self.set_up()
            self.is_setup = True
            self._log("初始化完成")

            # 2. 执行阶段
            self._log("开始执行...")
            self.start_time = datetime.now()
            res = self.execute()
            self.end_time = datetime.now()
            self.is_executed = True
            self._log("执行完成")

            # 3. 清理阶段
            self._log("开始清理...")
            self.set_down()
            self.is_teardown = True
            self._log("清理完成")

            return res

        except Exception as e:
            self._log(f"执行过程中发生错误: {str(e)}")
            # 确保即使出错也要尝试清理
            if self.is_setup and not self.is_teardown:
                try:
                    self.set_down()
                    self.is_teardown = True
                    self._log("错误后清理完成")
                except Exception as cleanup_error:
                    self._log(f"清理过程中发生错误: {str(cleanup_error)}")
            raise

    @abstractmethod
    def set_up(self):
        """
        初始化方法，子类必须实现
        用于设置执行环境、初始化资源等
        """
        pass

    @abstractmethod
    def execute(self) -> Any:
        """
        执行方法，子类必须实现
        执行具体的业务逻辑
        """
        pass

    @abstractmethod
    def set_down(self):
        """
        清理方法，子类必须实现
        用于清理资源、关闭连接等
        """
        pass

    def _log(self, message: str) :
        """
        内部日志方法
        """
        logger.info(f"[{self.name}] {message}")

    def get_execution_time(self) -> Optional[float]:
        """
        获取执行时间（秒）
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def get_status(self) -> Dict[str, Any]:
        """
        获取执行器状态
        """
        return {
            "name": self.name,
            "is_setup": self.is_setup,
            "is_executed": self.is_executed,
            "is_teardown": self.is_teardown,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.get_execution_time()
        }
