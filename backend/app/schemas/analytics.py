from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ScoreHistoryItem(BaseModel):
    interview_id: str
    date: str
    role: str
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float

class AnalyticsOverview(BaseModel):
    total_interviews: int
    average_score: float
    best_score: float
    resume_match_score: float
    technical_score: float
    communication_score: float
    recent_interviews: List[Dict[str, Any]]
    performance_trend: List[ScoreHistoryItem]
    skill_strengths: List[Dict[str, Any]]
    skill_gaps: List[Dict[str, Any]]
    recommended_practice: List[str]

class AnalyticsProgress(BaseModel):
    score_over_time: List[ScoreHistoryItem]
    category_averages: Dict[str, float]
    skill_radar: List[Dict[str, Any]]
    improvement_insights: List[str]
