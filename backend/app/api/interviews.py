from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.interview import Interview, InterviewQuestion
from app.models.evaluation import Answer, Evaluation, InterviewReport
from app.schemas.interview import (
    InterviewCreate, InterviewResponse, InterviewDetailResponse,
    QuestionResponse, AnswerSubmitRequest, AnswerResponse
)
from app.auth.deps import get_current_user
from app.ai.factory import get_ai_provider
from app.services.speech_analyzer import analyze_speech_transcript
from app.services.adaptive_engine import handle_adaptive_progression
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("", response_model=InterviewDetailResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    payload: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initializes an interview session and pre-generates grounded initial questions."""
    resume_text = None
    if payload.resume_id:
        resume = db.query(Resume).filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id).first()
        if resume:
            resume_text = resume.raw_text

    job_text = None
    if payload.job_id:
        job = db.query(JobDescription).filter(JobDescription.id == payload.job_id, JobDescription.user_id == current_user.id).first()
        if job:
            job_text = job.raw_text

    title = f"{payload.role} ({payload.interview_type})"
    if payload.company:
        title = f"{payload.company} - {title}"

    interview = Interview(
        user_id=current_user.id,
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        title=title,
        role=payload.role,
        company=payload.company,
        interview_type=payload.interview_type,
        difficulty=payload.difficulty,
        total_questions=payload.total_questions,
        duration_minutes=payload.duration_minutes,
        status="created",
        current_question_index=0
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # Generate personalized questions
    ai_provider = get_ai_provider()
    questions_data = ai_provider.generate_questions(
        role=payload.role,
        interview_type=payload.interview_type,
        difficulty=payload.difficulty,
        num_questions=payload.total_questions,
        resume_text=resume_text,
        job_text=job_text,
        company=payload.company
    )

    db_questions = []
    for q_item in questions_data:
        q_obj = InterviewQuestion(
            interview_id=interview.id,
            question_index=q_item.get("question_index", 1),
            question_text=q_item.get("question_text", "Describe your experience."),
            category=q_item.get("category", "Technical"),
            difficulty_level=q_item.get("difficulty_level", payload.difficulty),
            expected_key_points=q_item.get("expected_key_points", []),
            is_follow_up=q_item.get("is_follow_up", False),
            follow_up_reason=q_item.get("follow_up_reason")
        )
        db.add(q_obj)
        db_questions.append(q_obj)

    db.commit()

    questions_res = [QuestionResponse.model_validate(q) for q in db_questions]
    return InterviewDetailResponse(
        id=interview.id,
        title=interview.title,
        role=interview.role,
        company=interview.company,
        interview_type=interview.interview_type,
        difficulty=interview.difficulty,
        total_questions=interview.total_questions,
        duration_minutes=interview.duration_minutes,
        status=interview.status,
        current_question_index=interview.current_question_index,
        overall_score=interview.overall_score,
        created_at=interview.created_at,
        started_at=interview.started_at,
        completed_at=interview.completed_at,
        questions=questions_res,
        current_question=questions_res[0] if questions_res else None
    )

@router.get("", response_model=List[InterviewResponse])
def get_user_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all interview sessions created by the user."""
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc()).all()
    return [InterviewResponse.model_validate(i) for i in interviews]

@router.get("/{interview_id}", response_model=InterviewDetailResponse)
def get_interview_detail(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches full state of an interview room including question sequence."""
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview.id).order_by(InterviewQuestion.question_index.asc()).all()
    questions_res = [QuestionResponse.model_validate(q) for q in questions]

    current_q = None
    if 0 <= interview.current_question_index < len(questions_res):
        current_q = questions_res[interview.current_question_index]

    return InterviewDetailResponse(
        id=interview.id,
        title=interview.title,
        role=interview.role,
        company=interview.company,
        interview_type=interview.interview_type,
        difficulty=interview.difficulty,
        total_questions=interview.total_questions,
        duration_minutes=interview.duration_minutes,
        status=interview.status,
        current_question_index=interview.current_question_index,
        overall_score=interview.overall_score,
        created_at=interview.created_at,
        started_at=interview.started_at,
        completed_at=interview.completed_at,
        questions=questions_res,
        current_question=current_q
    )

@router.post("/{interview_id}/start", response_model=InterviewResponse)
def start_interview(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks interview as active in-progress session."""
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()
    db.commit()
    db.refresh(interview)
    return InterviewResponse.model_validate(interview)

@router.post("/{interview_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    interview_id: str,
    payload: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits answer, analyzes speech transcript for verbal fillers,
    evaluates using AI, triggers adaptive follow-up logic, and advances interview index.
    """
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == payload.question_id,
        InterviewQuestion.interview_id == interview.id
    ).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview question not found")

    # Perform Speech / Communication Analysis
    speech_stats = analyze_speech_transcript(
        payload.answer_text,
        duration_seconds=payload.audio_duration_seconds
    )

    # Persist candidate answer
    answer = Answer(
        interview_id=interview.id,
        question_id=question.id,
        answer_text=payload.answer_text.strip(),
        input_mode=payload.input_mode,
        audio_duration_seconds=payload.audio_duration_seconds,
        filler_words_count=speech_stats["filler_words_count"],
        filler_breakdown=speech_stats["filler_breakdown"],
        filler_frequency_pct=speech_stats["filler_frequency_pct"],
        words_count=speech_stats["words_count"],
        speech_pace_wpm=speech_stats["speech_pace_wpm"],
        communication_indicators=speech_stats["communication_indicators"]
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    # Evaluate Answer with AI Provider
    ai_provider = get_ai_provider()
    eval_data = ai_provider.evaluate_answer(
        question_text=question.question_text,
        category=question.category,
        difficulty=question.difficulty_level,
        answer_text=payload.answer_text,
        expected_points=question.expected_key_points
    )

    eval_obj = Evaluation(
        interview_id=interview.id,
        question_id=question.id,
        answer_id=answer.id,
        technical_accuracy=eval_data.get("technical_accuracy", 7.0),
        relevance=eval_data.get("relevance", 7.0),
        completeness=eval_data.get("completeness", 7.0),
        clarity=eval_data.get("clarity", 7.0),
        problem_solving=eval_data.get("problem_solving", 7.0),
        overall_score=eval_data.get("overall_score", 7.0),
        strengths=eval_data.get("strengths", []),
        weaknesses=eval_data.get("weaknesses", []),
        feedback=eval_data.get("feedback"),
        ideal_answer=eval_data.get("ideal_answer"),
        next_difficulty_adjustment=eval_data.get("next_difficulty_adjustment", "maintain"),
        recommended_follow_up=eval_data.get("recommended_follow_up")
    )
    db.add(eval_obj)

    # Trigger Adaptive Progression
    handle_adaptive_progression(
        interview=interview,
        current_question=question,
        candidate_answer=payload.answer_text,
        evaluation_data=eval_data,
        db=db
    )

    # Advance Question Index
    interview.current_question_index += 1
    total_q = interview.total_questions

    # If reached or exceeded total questions, mark as complete and create report
    if interview.current_question_index >= total_q:
        interview.status = "completed"
        interview.completed_at = datetime.utcnow()
        
        # Calculate overall interview score
        all_evals = db.query(Evaluation).filter(Evaluation.interview_id == interview.id).all()
        if all_evals:
            avg_sc = sum(e.overall_score for e in all_evals) / len(all_evals)
            interview.overall_score = round(avg_sc * 10, 1)

        # Generate final report automatically
        _generate_interview_report(interview, db, ai_provider)

    db.commit()

    # Broadcast real-time event to WebSocket room
    await ws_manager.broadcast_to_room(interview.id, {
        "event": "answer_evaluated",
        "question_index": question.question_index,
        "next_index": interview.current_question_index,
        "is_completed": interview.status == "completed"
    })

    return AnswerResponse(
        id=answer.id,
        question_id=answer.question_id,
        answer_text=answer.answer_text,
        input_mode=answer.input_mode,
        filler_words_count=answer.filler_words_count,
        filler_breakdown=answer.filler_breakdown,
        filler_frequency_pct=answer.filler_frequency_pct,
        words_count=answer.words_count,
        speech_pace_wpm=answer.speech_pace_wpm,
        communication_indicators=answer.communication_indicators
    )

@router.post("/{interview_id}/complete", response_model=InterviewResponse)
def complete_interview(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually completes interview and synthesizes final report."""
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

    interview.status = "completed"
    interview.completed_at = datetime.utcnow()

    ai_provider = get_ai_provider()
    all_evals = db.query(Evaluation).filter(Evaluation.interview_id == interview.id).all()
    if all_evals:
        avg_sc = sum(e.overall_score for e in all_evals) / len(all_evals)
        interview.overall_score = round(avg_sc * 10, 1)

    _generate_interview_report(interview, db, ai_provider)
    db.commit()
    db.refresh(interview)

    return InterviewResponse.model_validate(interview)

def _generate_interview_report(interview: Interview, db: Session, ai_provider):
    """Synthesizes all evaluations into InterviewReport record."""
    existing_rep = db.query(InterviewReport).filter(InterviewReport.interview_id == interview.id).first()
    if existing_rep:
        return existing_rep

    answers = db.query(Answer).filter(Answer.interview_id == interview.id).all()
    evals = db.query(Evaluation).filter(Evaluation.interview_id == interview.id).all()
    
    perf_records = []
    for ev in evals:
        perf_records.append({
            "evaluation": {
                "overall_score": ev.overall_score,
                "technical_accuracy": ev.technical_accuracy,
                "clarity": ev.clarity,
                "problem_solving": ev.problem_solving,
                "strengths": ev.strengths,
                "weaknesses": ev.weaknesses
            }
        })

    report_data = ai_provider.generate_report(
        interview_data={"role": interview.role, "type": interview.interview_type},
        answers_and_evaluations=perf_records
    )

    report = InterviewReport(
        interview_id=interview.id,
        user_id=interview.user_id,
        overall_score=report_data.get("overall_score", 78.0),
        technical_score=report_data.get("technical_score", 80.0),
        communication_score=report_data.get("communication_score", 76.0),
        problem_solving_score=report_data.get("problem_solving_score", 78.0),
        behavioral_score=report_data.get("behavioral_score", 76.0),
        resume_match_score=report_data.get("resume_match_score", 85.0),
        interview_readiness=report_data.get("interview_readiness", "Moderate"),
        key_strengths=report_data.get("key_strengths", []),
        weak_areas=report_data.get("weak_areas", []),
        recommended_topics=report_data.get("recommended_topics", []),
        prep_plan=report_data.get("prep_plan", []),
        detailed_summary=report_data.get("detailed_summary", "Assessment concluded.")
    )
    db.add(report)
    db.commit()
    return report
