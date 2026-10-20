from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, model_validator

class ParsedResumeData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[Dict[str, Any]] = []
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    achievements: List[str] = []
    summary: Optional[str] = None

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: Optional[str] = "pdf"
    file_path: Optional[str] = None
    skills: List[str] = []
    parsed_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    success: bool = True
    message: str = "Resume uploaded successfully"
    resume_id: Optional[str] = None
    parsed: bool = True

    @model_validator(mode="after")
    def set_computed_fields(self):
        if not self.resume_id:
            self.resume_id = self.id
        return self

    model_config = {"from_attributes": True}

class ResumeListResponse(BaseModel):
    id: str
    filename: str
    skills_count: int
    top_skills: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}
