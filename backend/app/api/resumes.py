import os
import re
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeListResponse
from app.auth.deps import get_current_user
from app.services.resume_parser import parse_resume_content
from app.ai.factory import get_ai_provider
from app.config import settings

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads, validates, extracts, parses, and persists candidate resume."""
    filename = file.filename or "resume.pdf"
    
    # 1. Validate file extension (.pdf, .docx only)
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Only PDF and DOCX files are supported."
        )

    # 2. Validate MIME / Content-Type
    allowed_mimes = {
        "application/pdf",
        "application/x-pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/octet-stream"
    }
    content_type = (file.content_type or "").lower().strip()
    if content_type and content_type not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file MIME type '{content_type}'. Only PDF and DOCX files are supported."
        )

    # 3. Read bytes with file size guard (413 Payload Too Large)
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty. Please select a valid resume."
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # 4. Safe Storage (Prevent path traversal, store in backend/uploads/resumes/)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.path.join(base_dir, "uploads", "resumes")
    os.makedirs(upload_dir, exist_ok=True)

    clean_filename = os.path.basename(filename)
    safe_name = re.sub(r'[^a-zA-Z0-9_\.-]', '_', clean_filename)
    resume_id = str(uuid.uuid4())
    stored_filename = f"{resume_id}_{safe_name}"
    file_path = os.path.join(upload_dir, stored_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error saving uploaded file: {str(e)}"
        )

    # 5. Parse resume content
    try:
        raw_text, parsed_data = parse_resume_content(file_bytes, filename)
    except ValueError as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Resume uploaded, but text extraction failed: {str(e)}"
        )
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server processing error during parsing: {str(e)}"
        )

    # 6. Generate semantic embedding
    ai_provider = get_ai_provider()
    embedding = ai_provider.generate_embedding(raw_text[:2000])

    # 7. Persist to Database with authenticated user_id
    file_type_str = ext.lstrip(".").lower()
    resume = Resume(
        id=resume_id,
        user_id=current_user.id,
        filename=clean_filename,
        file_path=file_path,
        file_type=file_type_str,
        raw_text=raw_text,
        parsed_data=parsed_data,
        skills=parsed_data.get("skills", []),
        embedding_vector=embedding
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeResponse(
        id=resume.id,
        user_id=resume.user_id,
        filename=resume.filename,
        file_type=resume.file_type or file_type_str,
        file_path=resume.file_path,
        skills=resume.skills or [],
        parsed_data=resume.parsed_data or {},
        created_at=resume.created_at,
        updated_at=resume.updated_at,
        success=True,
        message="Resume uploaded successfully",
        resume_id=resume.id,
        parsed=True
    )

@router.get("", response_model=List[ResumeListResponse])
def get_user_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves list of uploaded resumes for the current user."""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    results = []
    for r in resumes:
        skills = r.skills or []
        results.append(ResumeListResponse(
            id=r.id,
            filename=r.filename,
            skills_count=len(skills),
            top_skills=skills[:5],
            created_at=r.created_at
        ))
    return results

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume_by_id(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches full parsed details of a specific resume."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return ResumeResponse.model_validate(resume)
