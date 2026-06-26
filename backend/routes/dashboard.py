import json
from collections import Counter

from fastapi import APIRouter
from database.db import SessionLocal
from database.models import Application

router = APIRouter()

@router.get("/dashboard")
def dashboard():
    db = SessionLocal()
    applications = db.query(Application).all()

    total = len(applications)
    scores = [app.priority_score or 0 for app in applications]
    average_score = round(sum(scores) / total, 1) if total else 0
    high_priority = len([app for app in applications if app.priority_score >= 70])
    status_counts = Counter([app.status for app in applications])

    actions = []
    for app in applications:
        for task in app.tasks:
            if task.column_status in ["today", "thisWeek"]:
                actions.append(task.title)

    db.close()

    return {
        "applications": total,
        "high_priority_jobs": high_priority,
        "average_score": average_score,
        "status_counts": dict(status_counts),
        "next_actions": actions[:3]
    }
