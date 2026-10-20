from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class EvaluationResponse(BaseModel):
    id: str
    question_id: str
    answer_id: str
    technical_accuracy: float
    relevance: float
    completeness: float
    clarity: float
    problem_solving: float
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    feedback: Optional[str]
    ideal_answer: Optional[str]
    next_difficulty_adjustment: str
    recommended_follow_up: Optional[str]

    model_config = {"from_attributes": True}

class QuestionReviewItem(BaseModel):
    question_id: str
    question_index: int
    question_text: str
    category: str
    difficulty_level: str
    is_follow_up: bool
    candidate_answer: Optional[str] = None
    input_mode: Optional[str] = None
    evaluation: Optional[EvaluationResponse] = None
    filler_count: Optional[int] = 0
    filler_breakdown: Optional[Dict[str, int]] = None

class ReportResponse(BaseModel):
    interview_id: str
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    behavioral_score: float
    resume_match_score: float
    interview_readiness: str
    key_strengths: List[str]
    weak_areas: List[str]
    recommended_topics: List[str]
    prep_plan: List[str]
    detailed_summary: str
    total_questions: int
    answered_questions: int
    question_reviews: List[QuestionReviewItem] = []
    created_at: datetime
