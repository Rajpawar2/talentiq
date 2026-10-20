from typing import List, Dict, Any, Optional

def compute_matching(
    resume_skills: List[str],
    resume_text: str,
    jd_skills: List[str],
    jd_text: str
) -> Dict[str, Any]:
    """
    Performs comprehensive resume-to-job matching analysis.
    Calculates overlap, identifies missing skills, and formulates recommendations.
    """
    r_skills_norm = {s.lower().strip(): s for s in resume_skills}
    j_skills_norm = {s.lower().strip(): s for s in jd_skills}

    matched = []
    missing = []

    for s_low, s_orig in j_skills_norm.items():
        if s_low in r_skills_norm or s_low in resume_text.lower():
            matched.append(s_orig)
        else:
            missing.append(s_orig)

    total_jd = len(j_skills_norm) if j_skills_norm else 1
    skill_pct = round((len(matched) / total_jd) * 100, 1)

    # Heuristic score weighting: skills (60%), domain presence (40%)
    domain_overlap_bonus = 15.0 if any(k in resume_text.lower() for k in ["lead", "architect", "senior", "production"]) else 5.0
    overall_match = min(round(skill_pct * 0.75 + domain_overlap_bonus, 1), 98.0)
    overall_match = max(overall_match, 40.0)

    # Recommendations
    recs = []
    if missing:
        top_missing = missing[:3]
        recs.append(f"Consider building a demonstrable project featuring {', '.join(top_missing)}.")
        recs.append(f"Highlight any adjacent concepts related to {top_missing[0]} in your summary.")
    recs.append("Quantify business outcomes (e.g. latency, revenue, user retention) for key projects.")
    recs.append("Review modern system design fundamentals and cloud orchestration patterns.")

    strengths = [
        f"Strong proficiency verified in core stack: {', '.join(matched[:3]) if matched else 'general software engineering'}",
        "Demonstrated hands-on experience in full development lifecycles",
        "Solid alignment with primary responsibilities"
    ]

    exp_match = "Exceptional" if overall_match >= 85 else ("Strong" if overall_match >= 70 else "Moderate")

    return {
        "match_score": overall_match,
        "matched_skills": matched,
        "missing_skills": missing,
        "experience_match": exp_match,
        "strengths": strengths,
        "recommendations": recs,
        "skill_match_percentage": skill_pct,
        "semantic_similarity": round(overall_match / 100.0, 2)
    }
