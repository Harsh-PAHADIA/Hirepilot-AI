import json
import logging
from datetime import datetime

from services.lemma_provider import LemmaProvider, AI_ERROR_MESSAGE
from database.db import SessionLocal
from database.models import Application, ResumeProfile, Task, InterviewQuestion

logger = logging.getLogger(__name__)


def run_workflow(resume_text: str, jd_text: str):
    provider = LemmaProvider()

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_jd = executor.submit(provider.analyze_jd, jd_text)
        future_gap = executor.submit(provider.analyze_gap, resume_text, jd_text)
        future_score = executor.submit(provider.score_job, resume_text, jd_text)
        future_interview = executor.submit(provider.prepare_interview, resume_text, jd_text)

        jd_result = future_jd.result()
        gap_result = future_gap.result()
        score_result = future_score.result()
        interview_prep = future_interview.result()

    plan = provider.generate_plan(gap_result)

    db = SessionLocal()

    # 1. Create Resume Profile
    resume_profile = ResumeProfile(
        original_text=resume_text,
        strengths=json.dumps(gap_result.get("strengths", [])),
        weaknesses=json.dumps(gap_result.get("weaknesses", []))
    )
    db.add(resume_profile)
    db.flush()

    # 2. Create Application
    application = Application(
        resume_profile_id=resume_profile.id,
        company=jd_result.get("company") or "Unknown Company",
        role=jd_result.get("role") or "Unknown Role",
        status="Saved",
        priority_score=score_result.get("score") or 0,
        priority_level=score_result.get("priority_level") or "Unknown",
        interview_probability=score_result.get("interview_probability") or 0,
        match_reasoning=score_result.get("reason") or "",
        company_fit=gap_result.get("company_fit") or "",
        matched_skills=json.dumps(score_result.get("matched_skills", [])),
        missing_skills=json.dumps(score_result.get("missing_skills", []))
    )
    db.add(application)
    db.flush()

    # 3. Create Tasks — only save non-empty, non-error strings
    today_tasks = [
        t for t in plan.get("today", [])
        if t and str(t).strip() != AI_ERROR_MESSAGE
    ]
    week_tasks = [
        t for t in plan.get("this_week", [])
        if t and str(t).strip() != AI_ERROR_MESSAGE
    ]

    for title in today_tasks:
        db.add(Task(application_id=application.id, title=title, tag="Action Item", column_status="today"))

    for title in week_tasks:
        db.add(Task(application_id=application.id, title=title, tag="Action Item", column_status="thisWeek"))

    # 4. Create Interview Questions — only save valid, non-error questions
    saved_count = 0
    for q in (interview_prep or []):
        q_text = q.get("question") or q.get("q") or ""
        if not q_text.strip() or q_text.strip() == AI_ERROR_MESSAGE:
            logger.warning(f"Skipping saving invalid interview question: {q!r}")
            continue
        db.add(InterviewQuestion(
            application_id=application.id,
            category=q.get("category", "General"),
            difficulty=q.get("difficulty", "Medium"),
            question=q_text
        ))
        saved_count += 1

    if saved_count == 0:
        logger.warning("No valid interview questions were saved to the database.")

    db.commit()

    result = {
        "jd_analysis": jd_result,
        "gap_analysis": gap_result,
        "score": score_result,
        "plan": plan,
        "interview_prep": interview_prep or [],
        "application": {
            "id": application.id,
            "company": application.company,
            "role": application.role,
            "status": application.status,
            "priority_score": application.priority_score,
            "priority_level": application.priority_level,
            "interview_probability": application.interview_probability
        }
    }

    db.close()
    return result
