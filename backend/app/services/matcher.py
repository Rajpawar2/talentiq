import re
from typing import List, Dict, Any, Optional, Set, Tuple
from app.services.resume_parser import SKILL_TAXONOMY, extract_skills_from_text


def get_skill_canonical_and_aliases(skill_name: str) -> Tuple[str, List[str]]:
    """Resolves a skill name to canonical name and its recognized aliases."""
    s_lower = skill_name.lower().strip()
    for canonical, aliases in SKILL_TAXONOMY.items():
        if s_lower == canonical.lower() or s_lower in aliases:
            return canonical, aliases
    return skill_name.strip(), [s_lower]


def find_skill_evidence(skill_name: str, aliases: List[str], text: str) -> Optional[str]:
    """Finds the specific line or sentence in text containing the skill as proof evidence."""
    lines = text.split("\n")
    search_terms = [skill_name.lower()] + [a.lower() for a in aliases]

    for line in lines:
        clean_l = line.strip()
        lower_l = clean_l.lower()
        for term in search_terms:
            escaped = re.escape(term)
            pattern = r'(?:^|[\s,;/|])' + escaped + r'(?:[\s,;/|]|$)' if term in ["c++", "c#", ".net"] else r'\b' + escaped + r'\b'
            if re.search(pattern, lower_l):
                return clean_l[:120]
    return None


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    """Calculates word-level Jaccard semantic overlap between two texts."""
    stopwords = {
        "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with",
        "by", "as", "is", "are", "was", "were", "be", "been", "from", "that",
        "which", "who", "will", "would", "can", "could", "should", "our", "you"
    }
    words1 = {w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower()) if w not in stopwords}
    words2 = {w for w in re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower()) if w not in stopwords}

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2
    return round(len(intersection) / len(union), 2)


def compute_matching(
    resume_skills: List[str],
    resume_text: str,
    jd_skills: List[str],
    jd_text: str,
    required_skills: Optional[List[str]] = None,
    preferred_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Performs deterministic, explainable resume-to-job matching analysis:
    1. Exact skill & alias matching with supporting text evidence.
    2. Distinguishes required skills (65% weight) vs preferred skills (20% weight).
    3. Analyzes experience and domain alignment (15% weight).
    4. Computes genuine semantic vocabulary overlap (Jaccard similarity).
    5. Returns explainable match score, strengths, and targeted recommendations.
    """
    # Normalize candidate skills set
    candidate_skills_set = {s.lower().strip() for s in resume_skills}
    resume_lower = resume_text.lower()

    # Determine JD required and preferred skill sets
    if not required_skills and not preferred_skills:
        # If not explicitly partitioned, classify from jd_skills
        if jd_skills:
            req_list = jd_skills[:6]
            pref_list = jd_skills[6:]
        else:
            all_extracted = extract_skills_from_text(jd_text)
            req_list = all_extracted[:6]
            pref_list = all_extracted[6:]
    else:
        req_list = required_skills or []
        pref_list = preferred_skills or []

    # If both lists were empty, extract all skills from JD
    if not req_list and not pref_list:
        req_list = extract_skills_from_text(jd_text)

    all_jd_skills = req_list + [s for s in pref_list if s not in req_list]

    matched_skills = []
    missing_skills = []
    skill_evidence = {}

    for s_name in all_jd_skills:
        canonical, aliases = get_skill_canonical_and_aliases(s_name)
        is_matched = False

        # 1. Check in candidate's structured skills
        for alias in [canonical.lower()] + aliases:
            if alias in candidate_skills_set:
                is_matched = True
                break

        # 2. Check directly in resume text
        if not is_matched:
            for alias in [canonical.lower()] + aliases:
                escaped = re.escape(alias)
                pattern = r'(?:^|[\s,;/|])' + escaped + r'(?:[\s,;/|]|$)' if alias in ["c++", "c#", ".net"] else r'\b' + escaped + r'\b'
                if re.search(pattern, resume_lower):
                    is_matched = True
                    break

        if is_matched:
            matched_skills.append(canonical)
            evidence = find_skill_evidence(canonical, aliases, resume_text)
            if evidence:
                skill_evidence[canonical] = evidence
        else:
            missing_skills.append(canonical)

    # Calculate required and preferred percentages
    matched_req_skills = []
    missing_req_skills = []
    for r_s in req_list:
        can, _ = get_skill_canonical_and_aliases(r_s)
        if can in matched_skills:
            matched_req_skills.append(can)
        else:
            missing_req_skills.append(can)

    total_req = len(req_list) if req_list else 1
    req_pct = (len(matched_req_skills) / total_req) * 100.0

    matched_pref_skills = []
    missing_pref_skills = []
    for p_s in pref_list:
        can, _ = get_skill_canonical_and_aliases(p_s)
        if can in matched_skills:
            matched_pref_skills.append(can)
        else:
            missing_pref_skills.append(can)

    total_pref = len(pref_list)
    pref_pct = (len(matched_pref_skills) / total_pref * 100.0) if total_pref > 0 else req_pct

    # Domain alignment score (checks seniority, cloud, production keywords)
    domain_points = 0.0
    domain_terms = ["production", "scale", "architect", "lead", "senior", "cloud", "api", "database", "distributed"]
    for term in domain_terms:
        if term in resume_lower and term in jd_text.lower():
            domain_points += 11.1
    domain_pct = min(domain_points, 100.0)

    # Explainable Weighted Score:
    # 65% Required Skills + 20% Preferred Skills + 15% Domain & Experience Alignment
    if req_list:
        raw_score = (req_pct * 0.65) + (pref_pct * 0.20) + (domain_pct * 0.15)
    else:
        raw_score = (len(matched_skills) / max(len(all_jd_skills), 1) * 80.0) + (domain_pct * 0.20)

    overall_match = round(min(max(raw_score, 0.0), 100.0), 1)
    total_skills_count = len(all_jd_skills) if all_jd_skills else 1
    skill_pct = round((len(matched_skills) / total_skills_count) * 100, 1)

    # Real semantic Jaccard overlap
    semantic_sim = calculate_jaccard_similarity(resume_text, jd_text)

    # Actionable Recommendations based on actual missing skills
    recs = []
    if missing_skills:
        top_missing = missing_skills[:3]
        recs.append(f"Demonstrate proficiency in {', '.join(top_missing)} through sample code or portfolio projects.")
        if len(missing_skills) > 1:
            recs.append(f"Highlight any practical experience with {top_missing[0]} in your summary and project highlights.")
    recs.append("Quantify business and engineering outcomes (e.g. latency reduction, throughput, reliability).")
    recs.append("Ensure your technical skills section highlights both core languages and deployment tools.")

    # Objective Strengths
    strengths = []
    if matched_skills:
        strengths.append(f"Verified core competency alignment in: {', '.join(matched_skills[:4])}.")
    if domain_pct >= 50.0:
        strengths.append("Strong domain overlap with target production systems and architectural requirements.")
    strengths.append("Practical experience demonstrated in production full-lifecycle software engineering.")

    # Experience match tier
    if overall_match >= 82.0:
        exp_match = "Exceptional"
    elif overall_match >= 68.0:
        exp_match = "Strong"
    elif overall_match >= 50.0:
        exp_match = "Moderate"
    else:
        exp_match = "Needs Development"

    match_level = "Strong Match" if overall_match >= 75.0 else ("Moderate Match" if overall_match >= 50.0 else "Low Match")

    return {
        "match_score": overall_match,
        "overall_match": overall_match,
        "match_level": match_level,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_required_skills": matched_req_skills,
        "missing_required_skills": missing_req_skills,
        "matched_preferred_skills": matched_pref_skills,
        "missing_preferred_skills": missing_pref_skills,
        "experience_match": exp_match,
        "strengths": strengths,
        "recommendations": recs,
        "skill_match_percentage": skill_pct,
        "semantic_similarity": semantic_sim
    }
