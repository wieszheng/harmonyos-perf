# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/3 22:19
@Author   : wieszheng
@Software : PyCharm
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class DeviceInfo(BaseModel):
    __tablename__ = "device_info"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True)
    os_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class Apps(BaseModel):
    __tablename__ = "apps"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    package_name = Column(String, nullable=False, index=True)
    version = Column(String, nullable=True)
    app_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class TestRuns(BaseModel):
    __tablename__ = "test_runs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(Integer, nullable=False, index=True)
    app_id = Column(Integer, nullable=False, index=True)
    scenario_name = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, default=datetime.datetime.now, nullable=True)
    duration = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class MonitorData(BaseModel):
    __tablename__ = "monitor_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_run_id = Column(Integer, nullable=False, index=True)
    timestamp = Column(String, nullable=False)
    cpu_usage = Column(JSON, nullable=True)
    cpu_freq = Column(JSON, nullable=True)
    mem = Column(JSON, nullable=True)
    fps = Column(JSON, nullable=True)
