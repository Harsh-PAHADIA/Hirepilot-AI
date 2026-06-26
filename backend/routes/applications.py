from fastapi import APIRouter
from pydantic import BaseModel
from database.db import SessionLocal
from database.models import Application

router = APIRouter()

class ApplicationStatusUpdate(BaseModel):
    status: str

@router.get("/applications")
def get_applications():
    db = SessionLocal()
    applications = db.query(Application).all()
    
    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "company": app.company,
            "role": app.role,
            "status": app.status,
            "priority_score": app.priority_score,
            "priority_level": app.priority_level
        })
        
    db.close()
    return result

@router.put("/applications/{app_id}/status")
def update_application_status(app_id: int, update: ApplicationStatusUpdate):
    db = SessionLocal()
    app = db.query(Application).filter(Application.id == app_id).first()
    if app:
        app.status = update.status
        db.commit()
        db.refresh(app)
    db.close()
    return {"success": True}