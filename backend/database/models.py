from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ResumeProfile(Base):
    __tablename__ = "resume_profiles"
    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    strengths = Column(Text, nullable=True) # JSON
    weaknesses = Column(Text, nullable=True) # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    applications = relationship("Application", back_populates="resume_profile", cascade="all, delete-orphan")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    resume_profile_id = Column(Integer, ForeignKey("resume_profiles.id"), nullable=True)
    
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Saved") # Saved, Applied, Online Assessment, Interview, Final Round, Offer, Rejected
    
    priority_score = Column(Integer, nullable=False, default=0)
    priority_level = Column(String, default="Low") # High, Medium, Low
    interview_probability = Column(Integer, default=0)
    match_reasoning = Column(Text, nullable=True)
    company_fit = Column(Text, nullable=True)
    
    matched_skills = Column(Text, nullable=True) # JSON
    missing_skills = Column(Text, nullable=True) # JSON
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resume_profile = relationship("ResumeProfile", back_populates="applications")
    tasks = relationship("Task", back_populates="application", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="application", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    title = Column(String, nullable=False)
    tag = Column(String, nullable=True)
    column_status = Column(String, nullable=False, default="today") # today, thisWeek, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    application = relationship("Application", back_populates="tasks")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    category = Column(String, nullable=False) # DSA, SQL, Backend, Frontend, Behavioral, etc.
    difficulty = Column(String, nullable=False) # Easy, Medium, Hard, etc.
    question = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    application = relationship("Application", back_populates="interview_questions")

class Analytics(Base):
    __tablename__ = "analytics"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False) # YYYY-MM-DD
    total_applications = Column(Integer, default=0)
    average_match_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)