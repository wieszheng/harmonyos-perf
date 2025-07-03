import sqlite3
from typing import List, Dict, Any, Optional

DB_PATH = 'history.db'

class HistoryDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS version (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT,
            date TEXT,
            score INTEGER
        )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS metric (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER,
            title TEXT,
            value REAL,
            unit TEXT,
            FOREIGN KEY(version_id) REFERENCES version(id)
        )''')
        conn.commit()
        conn.close()

    def insert_version(self, version: str, date: str, score: int, metrics: List[Dict[str, Any]]):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO version (version, date, score) VALUES (?, ?, ?)", (version, date, score))
        version_id = c.lastrowid
        for metric in metrics:
            c.execute(
                "INSERT INTO metric (version_id, title, value, unit) VALUES (?, ?, ?, ?)",
                (version_id, metric['title'], metric['value'], metric['unit'])
            )
        conn.commit()
        conn.close()

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        sql = "SELECT id, version, date, score FROM version ORDER BY date DESC"
        if limit:
            sql += f" LIMIT {limit}"
        c.execute(sql)
        versions = c.fetchall()
        history = []
        for v in versions:
            version_id, version, date, score = v
            c.execute("SELECT title, value, unit FROM metric WHERE version_id=? ORDER BY id", (version_id,))
            metrics = [
                {"title": row[0], "value": row[1], "unit": row[2]} for row in c.fetchall()
            ]
            history.append({
                "version": version,
                "date": date,
                "score": score,
                "metrics": metrics
            })
        conn.close()
        return history

    def clear(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM metric")
        c.execute("DELETE FROM version")
        conn.commit()
        conn.close()

# 使用示例：
db = HistoryDB()
db.insert_version('v2.1.3', '2025-07-01', 85, [
    {"title": "应用启动", "value": 1.2, "unit": "s"},
    {"title": "内存使用", "value": 156, "unit": "MB"},
])
history = db.get_history()
print(history)


from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from typing import List, Dict, Any, Optional
import os

DB_PATH = 'history.db'
Base = declarative_base()

class Version(Base):
    __tablename__ = 'version'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String)
    date = Column(String)
    score = Column(Integer)
    metrics = relationship('Metric', back_populates='version', cascade='all, delete-orphan')

class Metric(Base):
    __tablename__ = 'metric'
    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey('version.id'))
    title = Column(String)
    value = Column(Float)
    unit = Column(String)
    version = relationship('Version', back_populates='metrics')

class HistoryDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        db_url = f'sqlite:///{self.db_path}'
        self.engine = create_engine(db_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, future=True)

    def insert_version(self, version: str, date: str, score: int, metrics: List[Dict[str, Any]]):
        session = self.Session()
        try:
            v = Version(version=version, date=date, score=score)
            for metric in metrics:
                m = Metric(title=metric['title'], value=metric['value'], unit=metric['unit'])
                v.metrics.append(m)
            session.add(v)
            session.commit()
        finally:
            session.close()

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        session = self.Session()
        try:
            q = session.query(Version).order_by(Version.date.desc())
            if limit:
                q = q.limit(limit)
            versions = q.all()
            history = []
            for v in versions:
                metrics = [
                    {"title": m.title, "value": m.value, "unit": m.unit}
                    for m in v.metrics
                ]
                history.append({
                    "version": v.version,
                    "date": v.date,
                    "score": v.score,
                    "metrics": metrics
                })
            return history
        finally:
            session.close()

    def clear(self):
        session = self.Session()
        try:
            session.query(Metric).delete()
            session.query(Version).delete()
            session.commit()
        finally:
            session.close()

# 使用示例：
if __name__ == '__main__':
    db = HistoryDB()
    db.insert_version('v2.1.3', '2025-07-01', 85, [
        {"title": "应用启动", "value": 1.2, "unit": "s"},
        {"title": "内存使用", "value": 156, "unit": "MB"},
    ])
    history = db.get_history()
    print(history)