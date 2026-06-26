from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routes.dashboard import router as dashboard_router
from routes.applications import router as applications_router
from routes.interview import router as interview_router
from routes.tasks import router as tasks_router
from routes.analytics import router as analytics_router

from workflows.placement_workflow import run_workflow

from database.models import Base
from database.db import engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(dashboard_router)
app.include_router(applications_router)
app.include_router(interview_router)
app.include_router(tasks_router)
app.include_router(analytics_router)

class AnalyzeRequest(BaseModel):
    resume: str
    jd: str

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    result = run_workflow(
        resume_text=req.resume,
        jd_text=req.jd
    )
    return result


@app.get("/")
def home():
    return {
        "message": "HirePilot AI Running"
    }
