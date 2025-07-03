from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from history_db import HistoryDB
from core.persistence.db import SQLPersister

icons = {
    "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>',
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"></rect><rect width="6" height="6" x="9" y="9" rx="1"></rect><path d="M15 2v2"></path><path d="M15 20v2"></path><path d="M2 15h2"></path><path d="M2 9h2"></path><path d="M20 15h2"></path><path d="M20 9h2"></path><path d="M9 2v2"></path><path d="M9 20v2"></path></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>',
    "monitor": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="3" rx="2"></rect><line x1="8" x2="16" y1="21" y2="21"></line><line x1="12" x2="12" y1="17" y2="21"></line></svg>',
    "thermometer": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"></path></svg>',
}

# 获取历史数据
db = SQLPersister()
history = db.get_history(limit=2)  # 取最近两个版本

# 当前版本和上一个版本
current = history[0] if len(history) > 0 else {}
previous = history[1] if len(history) > 1 else {}

# 计算每个指标的对比
metrics = []
for metric in current.get("metrics", []):
    title = metric["title"]
    value = metric["value"]
    unit = metric["unit"]
    # 查找上一个版本的同名指标
    prev_metric = next((m for m in previous.get("metrics", []) if m["title"] == title), None)
    if prev_metric:
        prev_value = prev_metric["value"]
        try:
            diff = value - prev_value
            if prev_value != 0:
                percent = (diff / prev_value) * 100
            else:
                percent = 0
            if diff > 0:
                trend = f"↑ {percent:+.0f}%"
                trend_type = "up"
            elif diff < 0:
                trend = f"↓ {percent:+.0f}%"
                trend_type = "down"
            else:
                trend = "—"
                trend_type = ""
        except Exception:
            trend = "—"
            trend_type = ""
    else:
        trend = "—"
        trend_type = ""
    metrics.append({
        "title": title,
        "value": value,
        "unit": unit,
        "target": metric.get("target", ""),
        "trend": trend,
        "trend_type": trend_type
    })

# 新增：读取fps均值并与目标值对比
fps_avg = db.get_fps_avg()  # 可加test_run_id参数
fps_target = 60
fps_trend = "达标" if fps_avg >= fps_target else "未达标"
metrics.append({
    "title": "FPS均值",
    "value": fps_avg,
    "unit": "",
    "target": fps_target,
    "trend": fps_trend,
    "trend_type": "up" if fps_avg >= fps_target else "down"
})

data = {
    "app_name": "文小言 App",
    "version": current.get("version", ""),
    "start_time": "12:00",
    "duration": "12",
    "score": current.get("score", 0),
    "score_up": current.get("score", 0) - previous.get("score", 0) if previous else 0,
    "metrics": metrics,
    "gen_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    "history": db.get_history(limit=5)
}

env = Environment(loader=FileSystemLoader('.'), autoescape=True)
template = env.get_template('performance_report_template.html')
html_content = template.render(**data)

with open('performance_report_template.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("报告已生成：performance_report.html") 