import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Answer(Base):
    __tablename__ = "answers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    answer_text = Column(Text, nullable=False)
    input_mode = Column(String(20), default="text")  # text | voice
    audio_duration_seconds = Column(Float, nullable=True)
    filler_words_count = Column(Integer, default=0)
    filler_breakdown = Column(JSON, default=dict)
    filler_frequency_pct = Column(Float, default=0.0)
    words_count = Column(Integer, default=0)
    speech_pace_wpm = Column(Float, nullable=True)
    communication_indicators = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="answers")
    question = relationship("InterviewQuestion", back_populates="answer")
    evaluation = relationship("Evaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    answer_id = Column(String, ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    
    technical_accuracy = Column(Float, default=0.0)
    relevance = Column(Float, default=0.0)
    completeness = Column(Float, default=0.0)
    clarity = Column(Float, default=0.0)
    problem_solving = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    feedback = Column(Text, nullable=True)
    ideal_answer = Column(Text, nullable=True)
    next_difficulty_adjustment = Column(String(30), default="maintain")  # increase, maintain, decrease
    recommended_follow_up = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="evaluations")
    question = relationship("InterviewQuestion", back_populates="evaluation")
    answer = relationship("Answer", back_populates="evaluation")


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    resume_match_score = Column(Float, default=0.0)
    interview_readiness = Column(String(50), default="Moderate")  # High, Moderate, Needs Preparation
    
    key_strengths = Column(JSON, default=list)
    weak_areas = Column(JSON, default=list)
    recommended_topics = Column(JSON, default=list)
    prep_plan = Column(JSON, default=list)
    detailed_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="report")
