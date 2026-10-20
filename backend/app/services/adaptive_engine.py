from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.interview import Interview, InterviewQuestion
from app.models.evaluation import Evaluation
from app.ai.factory import get_ai_provider

def handle_adaptive_progression(
    interview: Interview,
    current_question: InterviewQuestion,
    candidate_answer: str,
    evaluation_data: Dict[str, Any],
    db: Session
) -> Optional[InterviewQuestion]:
    """
    Evaluates current interview state and dynamically produces an adaptive question or
    adjusts subsequent questions based on candidate performance.
    """
    ai_provider = get_ai_provider()
    
    # Check if there are unasked pre-generated questions
    remaining_count = interview.total_questions - (interview.current_question_index + 1)
    
    if remaining_count <= 0:
        # Reached the end of interview questions
        return None

    # Check if we should insert an adaptive follow-up
    # Trigger follow-up when score is either very high (elevate) or very low (probe gap)
    overall_score = evaluation_data.get("overall_score", 7.0)
    should_follow_up = overall_score >= 8.5 or overall_score <= 5.5

    # Check next question in database
    next_question = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id == interview.id,
            InterviewQuestion.question_index == interview.current_question_index + 2
        )
        .first()
    )

    if should_follow_up:
        # Generate an adaptive follow-up
        follow_up_payload = ai_provider.generate_followup(
            previous_question=current_question.question_text,
            candidate_answer=candidate_answer,
            evaluation=evaluation_data,
            target_role=interview.role,
            remaining_questions=remaining_count
        )

        if next_question:
            # Adapt the next question directly into the follow up
            next_question.question_text = follow_up_payload.get("question_text", next_question.question_text)
            next_question.category = follow_up_payload.get("category", next_question.category)
            next_question.difficulty_level = follow_up_payload.get("difficulty_level", next_question.difficulty_level)
            next_question.is_follow_up = True
            next_question.follow_up_reason = follow_up_payload.get("follow_up_reason")
            next_question.expected_key_points = follow_up_payload.get("expected_key_points", [])
            db.commit()
            db.refresh(next_question)
            return next_question

    return next_question
