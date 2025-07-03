# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/7/3 22:21
@Author   : wieszheng
@Software : PyCharm
"""
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.persistence.models import Base, MonitorData, DeviceInfo, Apps, TestRuns

DB_PATH = 'history.db'


class SQLPersister:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        db_url = f'sqlite:///{self.db_path}'
        self.engine = create_engine(db_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_device_info(self, device_id, os_version=None):
        """
        保存设备信息
        """
        session = self.Session()
        try:
            res = DeviceInfo(device_id=device_id, os_version=os_version)
            session.add(res)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"写入数据库失败: {e}")
        finally:
            session.close()

    def get_device_id(self, device_id):
        """
        获取设备信息
        """
        session = self.Session()
        try:
            res = session.query(DeviceInfo).filter_by(device_id=device_id).first()
            return res.to_dict()
        finally:
            session.close()

    def save_app_info(self, package_name, version, app_name):
        """
        保存app信息
        """
        session = self.Session()
        try:
            res = Apps(package_name=package_name, version=version, app_name=app_name)
            session.add(res)
            session.commit()

        except Exception as e:
            session.rollback()
            print(f"写入数据库失败: {e}")
        finally:
            session.close()

    def get_app_id(self, package_name):
        """
        获取app信息
        """
        session = self.Session()
        try:
            res = session.query(Apps).filter_by(package_name=package_name).first()
            return res.to_dict()
        finally:
            session.close()

    def start_test_run(self, device_id, package_name, scenario_name):
        """
        更新开始时间
        """
        session = self.Session()
        try:
            # device_id = self.save_device_info(device_id)
            # app_id = self.save_app_info(package_name)
            app_id = 1
            res = TestRuns(device_id=device_id, app_id=app_id, scenario_name=scenario_name,
                           start_time=datetime.now())
            session.add(res)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"写入数据库失败: {e}")
        finally:
            session.close()

    def end_test_run(self, test_run_id, monitor_data):
        end_time = datetime.now()
        session = self.Session()
        try:
            res = session.query(TestRuns).filter_by(id=test_run_id).first()
            if res:
                duration = (datetime.now() - res.start_time)
                res.end_time = end_time
                res.duration = str(duration.seconds / 60)

                self.save_monitor_data(test_run_id=test_run_id, **monitor_data)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"写入数据库失败: {e}")
        finally:
            session.close()

    def save_monitor_data(self, test_run_id, cpu_usage, cpu_freq, mem, fps, timestamp):
        session = self.Session()
        try:
            record = MonitorData(
                test_run_id=test_run_id, cpu_usage=cpu_usage,
                cpu_freq=cpu_freq, mem=mem, fps=fps,
                timestamp=timestamp
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"写入数据库失败: {e}")
        finally:
            session.close()

    def get_fps_avg(self, test_run_id=None):

        session = Session()
        try:
            query = session.query(MonitorData)
            if test_run_id:
                query = query.filter(MonitorData.test_run_id == test_run_id)
            fps_values = []
            for row in query:
                # 假设fps字段为dict或float
                fps = row.fps
                if isinstance(fps, dict):
                    # 取主fps
                    fps_val = fps.get("fps", 0)
                else:
                    fps_val = float(fps)
                fps_values.append(fps_val)
            if fps_values:
                return round(sum(fps_values) / len(fps_values), 2)
            else:
                return 0
        finally:
            session.close()

    def get_mem_avg(self, test_run_id=None):
        session = self.Session()
        try:
            query = session.query(MonitorData)
            if test_run_id:
                query = query.filter(MonitorData.test_run_id == test_run_id)
            mem_values = []
            for row in query:
                mem = row.mem
                total = 0
                if isinstance(mem, dict):
                    total = sum(float(v) for v in mem.values() if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.', '', 1).isdigit()))
                elif isinstance(mem, str):
                    import json
                    try:
                        mem_dict = json.loads(mem)
                        total = sum(float(v) for v in mem_dict.values() if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.', '', 1).isdigit()))
                    except Exception:
                        total = 0
                mem_values.append(total)
            if mem_values:
                return round(sum(mem_values) / len(mem_values), 2)
            else:
                return 0
        finally:
            session.close()

if __name__ == '__main__':
    sql = SQLPersister()
    sql.start_test_run(1,1,"对话")
    data = {
        "cpu_usage": {"ad": 1.2, "bd": 1.3},
        "cpu_freq": {"ad": 1.2, "bd": 1.3},
        "mem": {"ad": 1.2, "bd": 1.3},
        "fps": {"ad": 1.2, "bd": 1.3},
        "timestamp": 122233,
    }
    sql.end_test_run(1, data)
