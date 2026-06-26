from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

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
    allow_origins=[
        "http://localhost:5173",
        "https://hirepilot-ai-two.vercel.app",
    ],
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
    logger.info("POST /analyze received")
    try:
        result = run_workflow(
            resume_text=req.resume,
            jd_text=req.jd
        )
        logger.info("POST /analyze completed successfully")
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"POST /analyze FAILED: {type(e).__name__}: {e}\n{tb}")
        raise HTTPException(
            status_code=503,
            detail=f"Analysis failed: {type(e).__name__}: {str(e)}"
        )


@app.get("/")
def home():
    return {
        "message": "HirePilot AI Running"
    }
