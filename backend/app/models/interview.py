import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(String, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    job_id = Column(String, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    role = Column(String(100), nullable=False)
    company = Column(String(100), nullable=True)
    interview_type = Column(String(50), default="Technical")  # Technical, Behavioral, Mixed, Coding
    difficulty = Column(String(20), default="Medium")          # Easy, Medium, Hard
    total_questions = Column(Integer, default=5)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(30), default="created")             # created, in_progress, completed, abandoned
    current_question_index = Column(Integer, default=0)
    overall_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    job_description = relationship("JobDescription", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan", order_by="InterviewQuestion.question_index")
    answers = relationship("Answer", back_populates="interview", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="interview", cascade="all, delete-orphan")
    report = relationship("InterviewReport", back_populates="interview", uselist=False, cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_index = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String(50), default="Technical")
    difficulty_level = Column(String(20), default="Medium")
    expected_key_points = Column(JSON, default=list)
    is_follow_up = Column(Boolean, default=False)
    follow_up_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")
    evaluation = relationship("Evaluation", back_populates="question", uselist=False, cascade="all, delete-orphan")
