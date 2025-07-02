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