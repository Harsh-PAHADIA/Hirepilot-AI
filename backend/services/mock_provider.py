import json
import random
from services.ai_provider import BaseAIProvider

class MockProvider(BaseAIProvider):
    """
    Mock AI Provider implementation. Acts as our current robust intelligence engine
    for the hackathon demo without needing fragile API keys.
    """

    def analyze_jd(self, jd_text: str) -> dict:
        text_lower = jd_text.lower()
        company = "Target Employer"
        role = "Target Role"
        if "google" in text_lower: company = "Google"
        elif "stripe" in text_lower: company = "Stripe"
        elif "vercel" in text_lower: company = "Vercel"
        elif "meta" in text_lower: company = "Meta"
        
        if "frontend" in text_lower or "react" in text_lower: role = "Frontend Engineer"
        elif "backend" in text_lower or "python" in text_lower: role = "Backend Engineer"
        elif "designer" in text_lower: role = "Product Designer"
        
        skills = self._extract_skills(text_lower)
        return {
            "company": company,
            "role": role,
            "required_skills": skills
        }

    def analyze_gap(self, resume_text: str, jd_text: str) -> dict:
        return {
            "missing_skills": ["System Design", "AWS", "GraphQL"],
            "suggestions": [
                "Highlight experience with scalable architectures.",
                "Review basic GraphQL concepts.",
                "Emphasize your recent complex engineering projects."
            ],
            "strengths": ["Project delivery", "Team collaboration", "Frontend expertise"],
            "weaknesses": ["Lack of cloud infrastructure experience", "Limited backend design"],
            "company_fit": "Strong culture fit. Technical gap in infrastructure."
        }

    def score_job(self, resume_text: str, jd_text: str) -> dict:
        score = random.randint(70, 95)
        interview_probability = random.randint(50, 90)
        return {
            "score": score,
            "interview_probability": interview_probability,
            "priority_level": "High" if score >= 85 else "Medium" if score >= 70 else "Low",
            "matched_skills": self._extract_skills(resume_text.lower() + " " + jd_text.lower())[:3],
            "missing_skills": ["System Design", "GraphQL"],
            "reason": f"Strong alignment with core requirements. The candidate has most of the required skills, leading to an estimated {score}% match."
        }

    def generate_plan(self, gap_analysis: dict) -> dict:
        return {
            "today": [
                "Tailor resume summary to highlight relevant keywords.",
                "Review top missing skills."
            ],
            "this_week": [
                "Complete a small project demonstrating missing skills.",
                "Prepare STAR method stories for behavioral questions."
            ]
        }

    def prepare_interview(self, resume_text: str, jd_text: str) -> list:
        return [
            {"category": "DSA", "difficulty": "Medium", "question": "Implement a LRU Cache"},
            {"category": "DSA", "difficulty": "Hard", "question": "Merge k Sorted Lists"},
            {"category": "SQL", "difficulty": "Medium", "question": "Find the Nth Highest Salary"},
            {"category": "Behavioral", "difficulty": "Medium", "question": "Tell me about a time you had a conflict with a coworker."},
            {"category": "System Design", "difficulty": "Hard", "question": "Design a scalable rate limiter."}
        ]

    def _extract_skills(self, text):
        tech_keywords = [
            "react", "python", "java", "c++", "sql", "fastapi", "node.js",
            "javascript", "typescript", "machine learning", "docker", "aws"
        ]
        found = set()
        for kw in tech_keywords:
            if kw in text:
                found.add(kw.title())
        return list(found)
