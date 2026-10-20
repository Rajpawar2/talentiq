from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.interview import Interview, InterviewQuestion
from app.models.evaluation import Answer, Evaluation, InterviewReport
from app.schemas.evaluation import ReportResponse, QuestionReviewItem, EvaluationResponse
from app.auth.deps import get_current_user
from app.ai.factory import get_ai_provider

router = APIRouter(prefix="", tags=["Evaluations & Reports"])

@router.get("/interviews/{interview_id}/report", response_model=ReportResponse)
def get_interview_report(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves or generates the comprehensive post-interview performance assessment report."""
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    # Fetch report or synthesize if missing
    report = db.query(InterviewReport).filter(InterviewReport.interview_id == interview.id).first()
    if not report:
        ai_provider = get_ai_provider()
        from app.api.interviews import _generate_interview_report
        report = _generate_interview_report(interview, db, ai_provider)

    # Fetch question-by-question breakdown
    questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview.id).order_by(InterviewQuestion.question_index.asc()).all()
    reviews = []
    answered_count = 0

    for q in questions:
        ans = db.query(Answer).filter(Answer.question_id == q.id).first()
        ev = db.query(Evaluation).filter(Evaluation.question_id == q.id).first()
        
        ev_schema = None
        if ev:
            ev_schema = EvaluationResponse.model_validate(ev)
            answered_count += 1

        reviews.append(QuestionReviewItem(
            question_id=q.id,
            question_index=q.question_index,
            question_text=q.question_text,
            category=q.category,
            difficulty_level=q.difficulty_level,
            is_follow_up=q.is_follow_up,
            candidate_answer=ans.answer_text if ans else None,
            input_mode=ans.input_mode if ans else None,
            evaluation=ev_schema,
            filler_count=ans.filler_words_count if ans else 0,
            filler_breakdown=ans.filler_breakdown if ans else {}
        ))

    return ReportResponse(
        interview_id=interview.id,
        overall_score=report.overall_score,
        technical_score=report.technical_score,
        communication_score=report.communication_score,
        problem_solving_score=report.problem_solving_score,
        behavioral_score=report.behavioral_score,
        resume_match_score=report.resume_match_score,
        interview_readiness=report.interview_readiness,
        key_strengths=report.key_strengths or [],
        weak_areas=report.weak_areas or [],
        recommended_topics=report.recommended_topics or [],
        prep_plan=report.prep_plan or [],
        detailed_summary=report.detailed_summary or "",
        total_questions=interview.total_questions,
        answered_questions=answered_count,
        question_reviews=reviews,
        created_at=report.created_at
    )
