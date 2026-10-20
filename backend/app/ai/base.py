from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class AIProvider(ABC):
    @abstractmethod
    def generate_questions(
        self,
        role: str,
        interview_type: str,
        difficulty: str,
        num_questions: int,
        resume_text: Optional[str] = None,
        job_text: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generates initial interview questions based on candidate profile and job requirements."""
        pass

    @abstractmethod
    def evaluate_answer(
        self,
        question_text: str,
        category: str,
        difficulty: str,
        answer_text: str,
        expected_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Evaluates candidate answer across technical and communication dimensions."""
        pass

    @abstractmethod
    def generate_followup(
        self,
        previous_question: str,
        candidate_answer: str,
        evaluation: Dict[str, Any],
        target_role: str,
        remaining_questions: int
    ) -> Dict[str, Any]:
        """Dynamically adapts the interview by producing a follow-up or next adaptive question."""
        pass

    @abstractmethod
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Extracts structured entities, skills, projects, and experiences from raw resume text."""
        pass

    @abstractmethod
    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Extracts required skills, experience level, responsibilities from job posting."""
        pass

    @abstractmethod
    def generate_report(
        self,
        interview_data: Dict[str, Any],
        answers_and_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesizes all evaluations into an overarching executive candidate report."""
        pass

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generates a dense vector embedding for semantic matching."""
        pass


class SpeechProvider(ABC):
    @abstractmethod
    def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        """Converts raw audio bytes into speech transcript text."""
        pass
