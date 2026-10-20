from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.interview import Interview, InterviewQuestion
from app.schemas.interview import QuestionResponse
from app.auth.deps import get_current_user

router = APIRouter(prefix="/interviews/{interview_id}/questions", tags=["Questions"])

@router.get("", response_model=List[QuestionResponse])
def get_interview_questions(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all generated questions for the specified interview."""
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview_id).order_by(InterviewQuestion.question_index.asc()).all()
    return [QuestionResponse.model_validate(q) for q in questions]
