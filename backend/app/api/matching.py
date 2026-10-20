from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.schemas.matching import MatchingRequest, MatchingResponse
from app.auth.deps import get_current_user
from app.services.matcher import compute_matching
from app.services.resume_parser import clean_extracted_text
from app.ai.factory import get_ai_provider

router = APIRouter(prefix="/matching", tags=["Matching"])

@router.post("/analyze", response_model=MatchingResponse)
def analyze_resume_job_match(
    payload: MatchingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compares candidate's resume with a target job description and generates match insights."""
    resume_text = ""
    resume_skills = []
    
    if payload.resume_id:
        resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
        resume_text = resume.raw_text
        resume_skills = resume.skills or []
    elif payload.resume_text:
        resume_text = clean_extracted_text(payload.resume_text)
        ai_provider = get_ai_provider()
        parsed = ai_provider.analyze_resume(resume_text)
        resume_skills = parsed.get("skills", [])
    else:
        # Default to latest resume of user
        resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
        if resume:
            resume_text = resume.raw_text
            resume_skills = resume.skills or []

    job_text = ""
    job_skills = []

    if payload.job_id:
        job = db.query(JobDescription).filter(JobDescription.id == payload.job_id, JobDescription.user_id == current_user.id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        job_text = job.raw_text
        job_skills = job.parsed_data.get("required_skills", []) + job.parsed_data.get("preferred_skills", [])
    elif payload.job_text:
        job_text = clean_extracted_text(payload.job_text)
        ai_provider = get_ai_provider()
        parsed = ai_provider.analyze_job_description(job_text)
        job_skills = parsed.get("required_skills", []) + parsed.get("preferred_skills", [])
    else:
        # Default to latest job of user
        job = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).first()
        if job:
            job_text = job.raw_text
            job_skills = job.parsed_data.get("required_skills", []) + job.parsed_data.get("preferred_skills", [])

    if not resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid resume (upload or ID) to run match analysis."
        )

    if not job_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid job description to run match analysis."
        )

    results = compute_matching(
        resume_skills=resume_skills,
        resume_text=resume_text,
        jd_skills=job_skills,
        jd_text=job_text
    )

    return MatchingResponse(**results)
