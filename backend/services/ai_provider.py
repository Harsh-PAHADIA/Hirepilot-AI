from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    """
    Interface for AI Providers.
    All future integrations (Lemma, Gemini, OpenAI) must implement this.
    """
    
    @abstractmethod
    def analyze_jd(self, jd_text: str) -> dict:
        pass
        
    @abstractmethod
    def analyze_gap(self, resume_text: str, jd_text: str) -> dict:
        pass
        
    @abstractmethod
    def score_job(self, resume_text: str, jd_text: str) -> dict:
        pass
        
    @abstractmethod
    def generate_plan(self, gap_analysis: dict) -> dict:
        pass
        
    @abstractmethod
    def prepare_interview(self, resume_text: str, jd_text: str) -> list:
        pass
