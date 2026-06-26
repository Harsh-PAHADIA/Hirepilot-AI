import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.lemma_provider import LemmaProvider

def test():
    print("Initializing LemmaProvider...")
    provider = LemmaProvider()
    
    sample_resume = """
    Jane Doe
    Senior Backend Engineer
    Experience:
    - 4 years at TechCorp. Built scalable microservices in Python, FastAPI, and Docker.
    - Designed Postgres databases and implemented CI/CD pipelines.
    Skills: Python, FastAPI, Docker, SQL, AWS, Kubernetes, React.
    """
    
    sample_jd = """
    Acme Inc is hiring a Senior Backend Engineer.
    Responsibilities:
    - Design and build RESTful APIs using Python and FastAPI.
    - Deploy containerized applications using Docker and Kubernetes.
    - Manage SQL databases.
    Qualifications:
    - 3+ years experience with Python.
    - Strong knowledge of backend architecture.
    """
    
    print("\n--- Testing JD Analysis (jd-analyst) ---")
    jd_res = provider.analyze_jd(sample_jd)
    print(json.dumps(jd_res, indent=2))
    
    print("\n--- Testing Resume & Gap Analysis (resume-analyst & gap-analyzer) ---")
    gap_res = provider.analyze_gap(sample_resume, sample_jd)
    print(json.dumps(gap_res, indent=2))
    
    print("\n--- Testing Match Scorer (match-scorer) ---")
    score_res = provider.score_job(sample_resume, sample_jd)
    print(json.dumps(score_res, indent=2))
    
    print("\n--- Testing Interview Prep (interview-coach) ---")
    interview_res = provider.prepare_interview(sample_resume, sample_jd)
    print(json.dumps(interview_res, indent=2))
    
    print("\n--- Testing Placement Planner (placement-planner) ---")
    plan_res = provider.generate_plan(gap_res)
    print(json.dumps(plan_res, indent=2))
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test()
