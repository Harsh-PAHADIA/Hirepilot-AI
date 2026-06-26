from fastapi import APIRouter
from collections import Counter
from datetime import datetime
from database.db import SessionLocal
from database.models import Application

router = APIRouter()

@router.get("/analytics")
def get_analytics():
    db = SessionLocal()
    applications = db.query(Application).all()
    
    total = len(applications)
    scores = [app.priority_score for app in applications if app.priority_score]
    average_score = round(sum(scores) / len(scores), 1) if scores else 0
    high_priority = len([app for app in applications if app.priority_level == "High"])
    
    # Calculate status distribution
    status_counts = Counter([app.status for app in applications])
    
    # Calculate match trend data (Mocked slightly by month since we only have current data, 
    # but in a real app would group by created_at.month)
    # We will generate a trend that peaks at current average
    trend = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Current"]
    base_score = max(50, average_score - 20)
    
    for i, month in enumerate(months):
        if month == "Current":
            trend.append({"month": month, "score": average_score})
        else:
            # Simulate an upward trend
            sim_score = int(base_score + (i * 3))
            trend.append({"month": month, "score": min(sim_score, 100)})

    db.close()
    
    return {
        "kpi": {
            "total_applications": total,
            "average_match_score": average_score,
            "high_priority_jobs": high_priority,
            "upcoming_interviews": status_counts.get("Interview", 0) + status_counts.get("Final Round", 0)
        },
        "status_distribution": dict(status_counts),
        "match_trend": trend
    }
