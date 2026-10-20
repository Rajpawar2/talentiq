from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    company: Optional[str] = "Tech Corp"
    raw_text: str = Field(..., min_length=20)

class ParsedJobData(BaseModel):
    title: str
    company: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_level: Optional[str] = None
    responsibilities: List[str] = []
    technologies: List[str] = []
    qualifications: List[str] = []

class JobResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: Optional[str]
    raw_text: str
    parsed_data: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
