import pytest
import io
from app.services.resume_parser import (
    clean_extracted_text, split_into_sections, extract_candidate_name,
    extract_contact_info, extract_skills_from_text, extract_education,
    extract_work_experience, extract_projects, extract_certifications,
    extract_text_from_pdf, extract_text_from_docx
)
from app.services.jd_parser import parse_job_description_content
from app.services.matcher import compute_matching
from app.services.speech_analyzer import analyze_speech_transcript
from app.services.adaptive_engine import handle_adaptive_progression
from app.models.interview import Interview, InterviewQuestion
from app.models.user import User
from app.database import SessionLocal, init_db
import uuid

SAMPLE_SWE_RESUME = """
Jane Doe
Senior Full-Stack Engineer
San Francisco, CA | (555) 234-5678 | jane.doe@example.com
linkedin.com/in/janedoe | github.com/janedoe | janedoe.dev

PROFESSIONAL SUMMARY
Results-driven engineer with 6+ years of experience designing scalable distributed backend microservices and modern React applications.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, Go, SQL
Frameworks & Libraries: FastAPI, Django, React, Node.js, Express, Next.js, Redux
Databases & Storage: PostgreSQL, Redis, MongoDB
DevOps & Cloud: AWS, Docker, Kubernetes, CI/CD, Git, Linux
Concepts: REST APIs, Microservices, System Design, GraphQL

WORK EXPERIENCE
Senior Software Engineer | Acme Cloud Corp | Jan 2021 - Present
- Architected asynchronous event-driven microservices using FastAPI and Redis, reducing p99 response times by 35%.
- Led database schema design and indexing in PostgreSQL, handling 20M+ daily transactions with 99.99% availability.
- Mentored junior engineers and instituted automated CI/CD testing pipelines.

Software Engineer | InnovateTech Labs | Jun 2018 - Dec 2020
- Built full-stack web applications using React, TypeScript, and Python Django.
- Developed real-time WebSocket communication channels for collaborative dashboard features.

PROJECTS
OpenSource Distributed Cache | 2023
- Implemented an in-memory key-value cache engine in Go with LRU eviction and consistent hashing.

Personal Portfolio & AI Code Assistant | 2022
- Created an interactive AI-powered code search tool using Next.js and vector embeddings.

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2014 - 2018

CERTIFICATIONS
AWS Certified Solutions Architect - Associate | 2022
Certified Kubernetes Administrator (CKA) | 2023
"""

SAMPLE_ACCOUNTANT_RESUME = """
Robert Clark
Certified Public Accountant
Chicago, IL | (312) 555-0199 | rclark@example.com

SUMMARY
Senior financial accountant with 8 years of corporate tax preparation, GAAP auditing, and general ledger reconciliation experience.

SKILLS
GAAP, Tax Planning, Financial Auditing, General Ledger, Payroll, QuickBooks, Excel Macros, SAP ERP

WORK EXPERIENCE
Senior Accountant | Midwest Financial Partners | 2019 - Present
- Conducted annual financial audits and tax filings for 40+ corporate clients.
- Managed quarterly reconciliations in SAP and QuickBooks.

EDUCATION
Bachelor of Science in Accounting
University of Illinois | 2011 - 2015
"""

SAMPLE_SWE_JD = """
Senior Backend Engineer - Distributed Systems
TechVanguard Inc. - San Francisco, CA

About the Role:
We are looking for a Senior Backend Engineer to build high-throughput microservices and data pipelines.

Required Skills:
- Python, FastAPI, PostgreSQL, Docker, Redis, Kubernetes

Preferred Skills:
- Go, GraphQL, AWS, Microservices

Qualifications:
- 5+ years of software engineering experience
- Bachelor's degree in Computer Science or equivalent practical experience
"""

# ==========================================================
# 1. RESUME PARSER & EXTRACTION ACCURACY TESTS
# ==========================================================

def test_resume_parser_name_extraction():
    cleaned = clean_extracted_text(SAMPLE_SWE_RESUME)
    lines = [l.strip() for l in cleaned.split("\n") if l.strip()]
    name = extract_candidate_name(cleaned, lines)
    assert name == "Jane Doe"


def test_resume_parser_contact_info():
    cleaned = clean_extracted_text(SAMPLE_SWE_RESUME)
    contact = extract_contact_info(cleaned)
    assert contact["email"] == "jane.doe@example.com"
    assert "555" in contact["phone"]
    assert "San Francisco" in contact["location"]
    assert "linkedin.com/in/janedoe" in contact["linkedin"]
    assert "github.com/janedoe" in contact["github"]
    assert "janedoe.dev" in contact["portfolio"]


def test_resume_parser_skills_and_normalization():
    cleaned = clean_extracted_text(SAMPLE_SWE_RESUME)
    sections = split_into_sections(cleaned)
    skills = extract_skills_from_text(sections["skills"] or cleaned)
    
    # Must capture core skills
    expected_skills = ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Kubernetes", "Redis", "TypeScript", "Go"]
    for s in expected_skills:
        assert s in skills, f"Skill '{s}' missing from parsed skills: {skills}"


def test_resume_parser_no_language_confusion():
    """Verify Java != JavaScript and C != C++"""
    text_with_js = "Experienced in JavaScript, React, and Node.js."
    skills_js = extract_skills_from_text(text_with_js)
    assert "JavaScript" in skills_js
    assert "Java" not in skills_js

    text_with_c = "Embedded programming in C and Assembly."
    skills_c = extract_skills_from_text(text_with_c)
    assert "C" in skills_c
    assert "C++" not in skills_c


def test_resume_parser_projects_not_classified_as_experience():
    cleaned = clean_extracted_text(SAMPLE_SWE_RESUME)
    sections = split_into_sections(cleaned)
    experience = extract_work_experience(sections["experience"])
    projects = extract_projects(sections["projects"])

    # Experience must contain employers, NOT projects
    exp_companies = [e.get("company", "").lower() for e in experience]
    for c in exp_companies:
        assert "opensource distributed cache" not in c
        assert "personal portfolio" not in c

    # Projects section must contain the projects
    proj_titles = [p.get("title", "").lower() for p in projects]
    assert any("cache" in t for t in proj_titles)


def test_resume_parser_certifications_not_degrees():
    cleaned = clean_extracted_text(SAMPLE_SWE_RESUME)
    sections = split_into_sections(cleaned)
    education = extract_education(sections["education"], cleaned)
    certs = extract_certifications(sections["certifications"], cleaned)

    # Education must contain degree, NOT AWS certification
    degrees = [ed.get("degree", "").lower() for ed in education]
    for d in degrees:
        assert "aws" not in d
        assert "kubernetes" not in d

    # Certs must contain AWS and CKA
    assert any("aws" in c.lower() for c in certs)
    assert any("cka" in c.lower() or "kubernetes" in c.lower() for c in certs)


# ==========================================================
# 2. JOB DESCRIPTION PARSING & MATCHING ACCURACY TESTS
# ==========================================================

def test_jd_parser_structured_extraction():
    jd_parsed = parse_job_description_content(SAMPLE_SWE_JD)
    assert "Senior Backend Engineer" in jd_parsed["title"]
    assert "TechVanguard" in jd_parsed["company"]
    
    req_skills = jd_parsed["required_skills"]
    assert "Python" in req_skills
    assert "FastAPI" in req_skills
    assert "PostgreSQL" in req_skills


def test_matcher_high_match_candidate():
    swe_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "Kubernetes", "Go", "AWS"]
    jd_parsed = parse_job_description_content(SAMPLE_SWE_JD)
    match_result = compute_matching(
        resume_skills=swe_skills,
        resume_text=SAMPLE_SWE_RESUME,
        jd_skills=jd_parsed.get("extracted_skills", []),
        jd_text=SAMPLE_SWE_JD,
        required_skills=jd_parsed.get("required_skills", []),
        preferred_skills=jd_parsed.get("preferred_skills", [])
    )

    assert match_result["overall_match"] >= 80.0
    assert len(match_result["matched_required_skills"]) >= 5
    assert len(match_result["missing_required_skills"]) == 0
    assert match_result["match_level"] == "Strong Match"


def test_matcher_zero_match_candidate():
    """An accountant applied to a senior distributed systems role must have 0.0% required skills match and no artificial 40% floor."""
    accountant_skills = ["GAAP", "Tax Planning", "QuickBooks", "SAP"]
    jd_parsed = parse_job_description_content(SAMPLE_SWE_JD)
    match_result = compute_matching(
        resume_skills=accountant_skills,
        resume_text=SAMPLE_ACCOUNTANT_RESUME,
        jd_skills=jd_parsed.get("extracted_skills", []),
        jd_text=SAMPLE_SWE_JD,
        required_skills=jd_parsed.get("required_skills", []),
        preferred_skills=jd_parsed.get("preferred_skills", [])
    )

    assert match_result["overall_match"] < 15.0
    assert match_result["matched_required_skills"] == []
    assert len(match_result["missing_required_skills"]) >= 5
    assert match_result["match_level"] == "Low Match"


# ==========================================================
# 3. SPEECH & COMMUNICATION ANALYSIS ACCURACY TESTS
# ==========================================================

def test_speech_analyzer_true_fillers():
    transcript = "Um, basically, our system was, like, architected using uh microservices and you know caching."
    stats = analyze_speech_transcript(transcript, duration_seconds=15.0)

    assert stats["filler_words_count"] >= 4
    assert stats["filler_frequency_pct"] > 10.0
    assert stats["speech_pace_wpm"] is not None
    assert stats["speech_pace_wpm"] > 0


def test_speech_analyzer_no_false_positives_for_so_and_right():
    """Words like 'so' and 'right' should not be counted as verbal fillers in natural speech."""
    clean_speech = "So we decided that the right solution was to implement database indexing and optimize query plans."
    stats = analyze_speech_transcript(clean_speech, duration_seconds=10.0)

    assert stats["filler_words_count"] == 0
    assert stats["filler_frequency_pct"] == 0.0


def test_speech_analyzer_exact_wpm_calculation():
    # 20 words spoken in 10 seconds => (20 / (10/60)) = 120 WPM
    words_20 = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty"
    stats = analyze_speech_transcript(words_20, duration_seconds=10.0)
    assert stats["speech_pace_wpm"] == 120.0
    assert stats["communication_indicators"]["pacing_assessment"] == "Optimal"


def test_speech_analyzer_text_mode_handles_none_duration():
    stats = analyze_speech_transcript("Here is my written response to the architectural question.", duration_seconds=None)
    assert stats["speech_pace_wpm"] is None
    assert "Text Response" in stats["communication_indicators"]["pacing_assessment"]


# ==========================================================
# 4. ADAPTIVE ENGINE ACCURACY TESTS
# ==========================================================

def test_adaptive_engine_escalates_on_high_score():
    db = SessionLocal()
    try:
        # Create user & interview session
        user = User(
            id=str(uuid.uuid4()),
            email=f"test_adaptive_{uuid.uuid4().hex[:6]}@example.com",
            name="Adaptive Test Candidate",
            hashed_password="hash"
        )
        db.add(user)
        db.commit()

        interview = Interview(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="Senior Distributed Systems Mock",
            role="Distributed Systems Engineer",
            interview_type="Technical",
            difficulty="Medium",
            total_questions=3,
            current_question_index=0
        )
        db.add(interview)
        db.commit()

        q1 = InterviewQuestion(
            id=str(uuid.uuid4()),
            interview_id=interview.id,
            question_index=1,
            question_text="How do you handle consistency in distributed transactions?",
            category="Technical",
            difficulty_level="Medium"
        )
        q2 = InterviewQuestion(
            id=str(uuid.uuid4()),
            interview_id=interview.id,
            question_index=2,
            question_text="Tell me about a challenging bug you fixed.",
            category="Technical",
            difficulty_level="Medium"
        )
        db.add_all([q1, q2])
        db.commit()

        # High scoring answer
        eval_data = {"overall_score": 9.0, "next_difficulty_adjustment": "increase"}
        adapted_q2 = handle_adaptive_progression(
            interview=interview,
            current_question=q1,
            candidate_answer="We utilized two-phase commit with idempotency keys and outbox pattern.",
            evaluation_data=eval_data,
            db=db
        )

        assert adapted_q2 is not None
        assert adapted_q2.difficulty_level == "Hard"
        assert adapted_q2.is_follow_up is True
        assert "distributed" in adapted_q2.follow_up_reason.lower() or "elevat" in adapted_q2.follow_up_reason.lower() or "score" in adapted_q2.follow_up_reason.lower()
    finally:
        db.close()


def test_adaptive_engine_deescalates_on_low_score():
    db = SessionLocal()
    try:
        user = User(
            id=str(uuid.uuid4()),
            email=f"test_adaptive_low_{uuid.uuid4().hex[:6]}@example.com",
            name="Adaptive Low Candidate",
            hashed_password="hash"
        )
        db.add(user)
        db.commit()

        interview = Interview(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="Junior Backend Mock",
            role="Backend Engineer",
            interview_type="Technical",
            difficulty="Medium",
            total_questions=3,
            current_question_index=0
        )
        db.add(interview)
        db.commit()

        q1 = InterviewQuestion(
            id=str(uuid.uuid4()),
            interview_id=interview.id,
            question_index=1,
            question_text="Explain how database connection pooling works under high load.",
            category="Technical",
            difficulty_level="Medium"
        )
        q2 = InterviewQuestion(
            id=str(uuid.uuid4()),
            interview_id=interview.id,
            question_index=2,
            question_text="Describe how you structure database migrations.",
            category="Technical",
            difficulty_level="Medium"
        )
        db.add_all([q1, q2])
        db.commit()

        # Low scoring answer
        eval_data = {"overall_score": 4.0, "next_difficulty_adjustment": "decrease"}
        adapted_q2 = handle_adaptive_progression(
            interview=interview,
            current_question=q1,
            candidate_answer="I am not sure how connections work.",
            evaluation_data=eval_data,
            db=db
        )

        assert adapted_q2 is not None
        assert adapted_q2.difficulty_level == "Easy"
        assert adapted_q2.is_follow_up is True
        assert "principles" in adapted_q2.follow_up_reason.lower() or "score" in adapted_q2.follow_up_reason.lower() or "prior answer" in adapted_q2.follow_up_reason.lower()
    finally:
        db.close()
