from fastapi import APIRouter
from collections import defaultdict
from database.db import SessionLocal
from database.models import InterviewQuestion
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

INVALID_VALUES = {"0", "null", "undefined", "none", "{}"}


@router.get("/interview-prep")
def get_interview_prep():
    db = SessionLocal()
    try:
        questions = db.query(InterviewQuestion).all()

        # Filter out invalid/garbage questions from the DB
        valid_questions = []
        for q in questions:
            q_text = str(q.question).strip() if q.question else ""
            if q_text and q_text.lower() not in INVALID_VALUES:
                valid_questions.append(q)
            else:
                logger.warning(f"Skipping invalid interview question id={q.id!r} text={q.question!r}")

        # Group by category
        grouped = defaultdict(list)
        for q in valid_questions:
            grouped[q.category].append({
                "id": q.id,
                "q": q.question,
                "difficulty": q.difficulty,
                "company": q.application.company if q.application else None
            })

        result = []
        for category, q_list in grouped.items():
            icon_name = "Code2"
            if "SQL" in category.upper():
                icon_name = "Database"
            elif "behavioral" in category.lower():
                icon_name = "Users"
            elif "company" in category.lower():
                icon_name = "Building2"

            result.append({
                "id": category.lower().replace(" ", "_"),
                "title": f"{category} Questions",
                "description": "Tailored questions for your applications",
                "icon_name": icon_name,
                "questions": q_list
            })

        return result
    finally:
        db.close()
