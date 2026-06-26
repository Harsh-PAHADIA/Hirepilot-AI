from fastapi import APIRouter
from pydantic import BaseModel
from database.db import SessionLocal
from database.models import Task

router = APIRouter()

class TaskStatusUpdate(BaseModel):
    column_status: str

@router.get("/tasks")
def get_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    
    result = {
        "today": [],
        "thisWeek": [],
        "completed": []
    }
    
    for t in tasks:
        col = t.column_status
        if col not in result:
            col = "today"
            
        result[col].append({
            "id": f"t-{t.id}",
            "db_id": t.id,
            "title": t.title,
            "tag": t.tag,
            "time": "Pending" if col != "completed" else "Done",
            "application_company": t.application.company if t.application else None
        })
        
    db.close()
    return result

@router.put("/tasks/{task_id}/status")
def update_task_status(task_id: int, update: TaskStatusUpdate):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.column_status = update.column_status
        db.commit()
        db.refresh(task)
    db.close()
    return {"success": True}
