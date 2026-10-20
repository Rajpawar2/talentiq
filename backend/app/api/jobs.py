from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.job_description import JobDescription
from app.schemas.job import JobCreate, JobResponse
from app.auth.deps import get_current_user
from app.services.jd_parser import parse_job_description_content
from app.services.resume_parser import clean_extracted_text, extract_text_from_pdf, extract_text_from_docx

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    payload: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Parses and saves a pasted job description."""
    try:
        parsed_data = parse_job_description_content(payload.raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse job description: {str(e)}"
        )

    job = JobDescription(
        user_id=current_user.id,
        title=payload.title.strip(),
        company=payload.company.strip() if payload.company else "Tech Corp",
        raw_text=payload.raw_text.strip(),
        parsed_data=parsed_data
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobResponse.model_validate(job)

@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_job_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads and parses a job description file (PDF, DOCX, TXT)."""
    filename = file.filename or "job_description.txt"
    file_bytes = await file.read()
    ext = filename.lower().split(".")[-1] if "." in filename else ""

    if ext == "pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raw_text = file_bytes.decode("utf-8", errors="ignore")

    raw_text = clean_extracted_text(raw_text)
    if not raw_text or len(raw_text) < 15:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not extract readable text from job file.")

    parsed_data = parse_job_description_content(raw_text)
    title = parsed_data.get("title", filename.split(".")[0])

    job = JobDescription(
        user_id=current_user.id,
        title=title,
        company=parsed_data.get("company", "Company"),
        raw_text=raw_text,
        parsed_data=parsed_data
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobResponse.model_validate(job)

@router.get("", response_model=List[JobResponse])
def get_user_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns all job descriptions submitted by the user."""
    jobs = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).all()
    return [JobResponse.model_validate(j) for j in jobs]

@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches details for a specific job description."""
    job = db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return JobResponse.model_validate(job)
