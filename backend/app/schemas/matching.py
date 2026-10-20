from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MatchingRequest(BaseModel):
    resume_id: Optional[str] = None
    job_id: Optional[str] = None
    resume_text: Optional[str] = None
    job_text: Optional[str] = None

class MatchingResponse(BaseModel):
    match_score: float = 0.0
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    experience_match: str = "Strong"
    strengths: List[str] = []
    recommendations: List[str] = []
    skill_match_percentage: float = 0.0
    semantic_similarity: float = 0.0
