from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.interview import Interview
from app.models.evaluation import InterviewReport, Evaluation
from app.models.resume import Resume
from app.schemas.analytics import AnalyticsOverview, AnalyticsProgress, ScoreHistoryItem
from app.auth.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview", response_model=AnalyticsOverview)
def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves top-level metrics, score distribution, and trends for candidate dashboard."""
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc()).all()
    reports = db.query(InterviewReport).filter(InterviewReport.user_id == current_user.id).order_by(InterviewReport.created_at.asc()).all()

    total_interviews = len(interviews)
    completed_reports = [r for r in reports if r.overall_score > 0]

    if completed_reports:
        avg_score = round(sum(r.overall_score for r in completed_reports) / len(completed_reports), 1)
        best_score = max([r.overall_score for r in completed_reports], default=0.0)

        tech_scores = [r.technical_score for r in completed_reports if r.technical_score > 0]
        avg_tech = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 0.0

        comm_scores = [r.communication_score for r in completed_reports if r.communication_score > 0]
        avg_comm = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else 0.0
    else:
        avg_score = 0.0
        best_score = 0.0
        avg_tech = 0.0
        avg_comm = 0.0

    # Resume Match Score
    resume_match = 0.0
    latest_resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).first()
    if latest_resume and latest_resume.skills:
        skill_count = len(latest_resume.skills)
        resume_match = min(round(skill_count * 5.0 + 30.0, 1), 92.0)

    # Performance trend list (authentic data only, never fake starter points)
    trend = []
    for r in completed_reports[-6:]:
        intv = db.query(Interview).filter(Interview.id == r.interview_id).first()
        trend.append(ScoreHistoryItem(
            interview_id=r.interview_id,
            date=r.created_at.strftime("%b %d"),
            role=intv.role if intv else "Candidate",
            overall_score=r.overall_score,
            technical_score=r.technical_score,
            communication_score=r.communication_score,
            problem_solving_score=r.problem_solving_score
        ))

    # Recent interview cards
    recent = []
    for i in interviews[:5]:
        recent.append({
            "id": i.id,
            "title": i.title,
            "role": i.role,
            "type": i.interview_type,
            "status": i.status,
            "score": i.overall_score or 0.0,
            "created_at": i.created_at.strftime("%Y-%m-%d %H:%M")
        })

    # Derive strengths & gaps from actual report evaluations
    skill_strengths = []
    skill_gaps = []
    recommended_practice = []

    if completed_reports:
        # Aggregate from candidate's reports
        seen_strengths = set()
        seen_weaknesses = set()

        for rep in completed_reports:
            for s in (rep.key_strengths or []):
                cleaned_s = s.strip()
                if cleaned_s and cleaned_s not in seen_strengths:
                    seen_strengths.add(cleaned_s)
                    skill_strengths.append({
                        "skill": cleaned_s[:35],
                        "level": min(int(rep.technical_score or 80), 95),
                        "status": "Strong"
                    })
                    if len(skill_strengths) >= 4:
                        break

            for w in (rep.weak_areas or []):
                cleaned_w = w.strip()
                if cleaned_w and cleaned_w not in seen_weaknesses:
                    seen_weaknesses.add(cleaned_w)
                    skill_gaps.append({
                        "skill": cleaned_w[:35],
                        "level": max(int((rep.overall_score or 65) - 15), 45),
                        "priority": "High" if len(skill_gaps) == 0 else "Medium"
                    })
                    if len(skill_gaps) >= 4:
                        break

            for p in (rep.prep_plan or []):
                if p not in recommended_practice:
                    recommended_practice.append(p)
                if len(recommended_practice) >= 3:
                    break

    if not recommended_practice:
        recommended_practice = [
            "Start your first mock interview to evaluate your technical and communication baseline.",
            "Upload your resume in Resume Intelligence to analyze technical skill coverage against job requirements.",
            "Practice timed problem decomposition to build structured answering confidence."
        ]

    return AnalyticsOverview(
        total_interviews=total_interviews,
        average_score=avg_score,
        best_score=best_score,
        resume_match_score=resume_match,
        technical_score=avg_tech,
        communication_score=avg_comm,
        recent_interviews=recent,
        performance_trend=trend,
        skill_strengths=skill_strengths,
        skill_gaps=skill_gaps,
        recommended_practice=recommended_practice
    )

@router.get("/progress", response_model=AnalyticsProgress)
def get_analytics_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves deep progression curves and radar metrics across categories."""
    reports = db.query(InterviewReport).filter(InterviewReport.user_id == current_user.id).order_by(InterviewReport.created_at.asc()).all()
    completed_reports = [r for r in reports if r.overall_score > 0]

    trend = []
    for r in completed_reports:
        intv = db.query(Interview).filter(Interview.id == r.interview_id).first()
        trend.append(ScoreHistoryItem(
            interview_id=r.interview_id,
            date=r.created_at.strftime("%b %d"),
            role=intv.role if intv else "Candidate",
            overall_score=r.overall_score,
            technical_score=r.technical_score,
            communication_score=r.communication_score,
            problem_solving_score=r.problem_solving_score
        ))

    if completed_reports:
        avg_tech = round(sum(r.technical_score for r in completed_reports) / len(completed_reports), 1)
        avg_comm = round(sum(r.communication_score for r in completed_reports) / len(completed_reports), 1)
        avg_ps = round(sum(r.problem_solving_score for r in completed_reports) / len(completed_reports), 1)
        avg_beh = round(sum(r.behavioral_score for r in completed_reports) / len(completed_reports), 1)

        radar = [
            {"subject": "Technical Depth", "score": int(avg_tech), "benchmark": 75},
            {"subject": "Communication", "score": int(avg_comm), "benchmark": 70},
            {"subject": "Problem Solving", "score": int(avg_ps), "benchmark": 75},
            {"subject": "Behavioral / STAR", "score": int(avg_beh), "benchmark": 72},
            {"subject": "Architecture", "score": int(avg_tech * 0.95), "benchmark": 70},
            {"subject": "Pacing & Clarity", "score": int(avg_comm * 0.98), "benchmark": 68},
        ]

        insights = []
        if len(completed_reports) > 1:
            first_score = completed_reports[0].overall_score
            latest_score = completed_reports[-1].overall_score
            diff = round(latest_score - first_score, 1)
            sign = "+" if diff >= 0 else ""
            insights.append(f"Overall performance changed by {sign}{diff} points across your completed mock sessions.")
        else:
            insights.append(f"Baseline established at {completed_reports[0].overall_score}% overall readiness.")

        latest_rep = completed_reports[-1]
        if latest_rep.key_strengths:
            insights.append(f"Key identified strength: {latest_rep.key_strengths[0]}")
        if latest_rep.weak_areas:
            insights.append(f"Primary area for improvement: {latest_rep.weak_areas[0]}")

    else:
        avg_tech = 0.0
        avg_comm = 0.0
        avg_ps = 0.0
        avg_beh = 0.0
        radar = [
            {"subject": "Technical Depth", "score": 0, "benchmark": 75},
            {"subject": "Communication", "score": 0, "benchmark": 70},
            {"subject": "Problem Solving", "score": 0, "benchmark": 75},
            {"subject": "Behavioral / STAR", "score": 0, "benchmark": 72},
            {"subject": "Architecture", "score": 0, "benchmark": 70},
            {"subject": "Pacing & Clarity", "score": 0, "benchmark": 68},
        ]
        insights = [
            "Complete your first adaptive interview to generate personalized multi-category progression curves.",
            "Your competency radar benchmarks your skills directly against senior engineering industry standards."
        ]

    return AnalyticsProgress(
        score_over_time=trend,
        category_averages={
            "technical": avg_tech,
            "communication": avg_comm,
            "problem_solving": avg_ps,
            "behavioral": avg_beh
        },
        skill_radar=radar,
        improvement_insights=insights
    )
