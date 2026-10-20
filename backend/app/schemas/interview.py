from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class InterviewCreate(BaseModel):
    role: str = Field(..., min_length=2, max_length=100)
    interview_type: str = Field("Technical", pattern="^(Technical|Behavioral|Mixed|Coding)$")
    difficulty: str = Field("Medium", pattern="^(Easy|Medium|Hard)$")
    total_questions: int = Field(5, ge=3, le=20)
    duration_minutes: int = Field(30, ge=10, le=120)
    resume_id: Optional[str] = None
    job_id: Optional[str] = None
    company: Optional[str] = None

class QuestionResponse(BaseModel):
    id: str
    question_index: int
    question_text: str
    category: str
    difficulty_level: str
    is_follow_up: bool
    follow_up_reason: Optional[str] = None

    model_config = {"from_attributes": True}

class AnswerSubmitRequest(BaseModel):
    question_id: str
    answer_text: str = Field(..., min_length=2)
    input_mode: str = Field("text", pattern="^(text|voice)$")
    audio_duration_seconds: Optional[float] = None

class AnswerResponse(BaseModel):
    id: str
    question_id: str
    answer_text: str
    input_mode: str
    filler_words_count: int
    filler_breakdown: Dict[str, int]
    filler_frequency_pct: float
    words_count: int
    speech_pace_wpm: Optional[float]
    communication_indicators: Dict[str, Any]

    model_config = {"from_attributes": True}

class InterviewResponse(BaseModel):
    id: str
    title: str
    role: str
    company: Optional[str]
    interview_type: str
    difficulty: str
    total_questions: int
    duration_minutes: int
    status: str
    current_question_index: int
    overall_score: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}

class InterviewDetailResponse(InterviewResponse):
    questions: List[QuestionResponse] = []
    current_question: Optional[QuestionResponse] = None
