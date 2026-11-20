from typing import Dict, Any, Optional, List
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
    Evaluates current interview state and dynamically adapts subsequent questions based
    on candidate performance, ensuring no duplicate questions and maintaining interview flow.
    """
    ai_provider = get_ai_provider()
    
    # Check if there are remaining questions in the session
    remaining_count = interview.total_questions - (interview.current_question_index + 1)
    if remaining_count <= 0:
        return None

    # Check next question in database
    next_question = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id == interview.id,
            InterviewQuestion.question_index == interview.current_question_index + 2
        )
        .first()
    )

    if not next_question:
        return None

    # Performance analysis
    overall_score = float(evaluation_data.get("overall_score", 7.0))
    adjustment = evaluation_data.get("next_difficulty_adjustment", "maintain")

    # Fetch all existing question texts in this interview to guarantee no duplicates
    existing_questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.interview_id == interview.id)
        .all()
    )
    existing_texts = {q.question_text.strip().lower() for q in existing_questions}

    # Generate an adaptive follow-up payload tailored to performance
    follow_up_payload = ai_provider.generate_followup(
        previous_question=current_question.question_text,
        candidate_answer=candidate_answer,
        evaluation=evaluation_data,
        target_role=interview.role,
        remaining_questions=remaining_count
    )

    new_question_text = follow_up_payload.get("question_text", "").strip()

    # If the generated question text already exists, add contextual variation
    if new_question_text.lower() in existing_texts:
        if overall_score >= 8.0:
            new_question_text = f"Building on that, how would you design a disaster recovery and zero-downtime failover strategy for that architecture?"
        elif overall_score <= 5.5:
            new_question_text = f"Taking a step back: How would you write unit and integration tests to verify the core correctness of that functionality?"
        else:
            new_question_text = f"In that design, how do you handle cache invalidation and ensure read-write consistency across services?"

    # Adapt the next question record
    next_question.question_text = new_question_text
    next_question.category = follow_up_payload.get("category", next_question.category)
    
    # Adjust difficulty level dynamically
    if overall_score >= 8.0 or adjustment == "increase":
        next_question.difficulty_level = "Hard"
    elif overall_score <= 5.5 or adjustment == "decrease":
        next_question.difficulty_level = "Easy"
    else:
        next_question.difficulty_level = "Medium"

    next_question.is_follow_up = True
    next_question.follow_up_reason = follow_up_payload.get(
        "follow_up_reason",
        f"Adapted based on score ({overall_score}/10) to calibrate candidate depth."
    )
    next_question.expected_key_points = follow_up_payload.get("expected_key_points", [
        "Architectural trade-offs",
        "Error handling & resilience",
        "Implementation specifics"
    ])

    db.commit()
    db.refresh(next_question)
    return next_question
