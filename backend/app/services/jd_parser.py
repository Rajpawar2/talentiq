import re
from typing import Dict, Any, List
from app.services.resume_parser import clean_extracted_text, extract_skills_from_text


def parse_job_description_content(jd_text: str) -> Dict[str, Any]:
    """
    Parses job description text and extracts title, company, required skills,
    preferred skills, experience level, responsibilities, and qualifications.
    """
    cleaned = clean_extracted_text(jd_text)
    if not cleaned or len(cleaned) < 15:
        raise ValueError("Job description is too brief. Please provide a more detailed job posting.")

    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]

    # 1. Job Title Extraction
    title = None
    title_match = re.search(r'(?:Job\s+Title|Position|Role|Title)\s*[:\-]\s*([A-Za-z0-9\s/().-]{3,50})', cleaned, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Check first 3 lines for a title-like line
        for line in lines[:3]:
            if any(role_w in line.lower() for role_w in ["engineer", "developer", "architect", "manager", "lead", "specialist", "scientist", "analyst"]):
                clean_title = re.split(r'[:|\-–—]', line)[0].strip()
                if len(clean_title.split()) <= 6:
                    title = clean_title
                    break
    if not title:
        title = lines[0][:50] if lines else "Software Engineer"

    # 2. Company Extraction
    company = None
    company_match = re.search(r'(?:Company|Organization|At)\s*[:\-]\s*([A-Za-z0-9\s.,&-]{2,40})', cleaned, re.IGNORECASE)
    if company_match:
        company = company_match.group(1).strip()
    else:
        hiring_match = re.search(r'\b([A-Z][a-zA-Z0-9\s]{1,25})\s+is\s+(?:hiring|looking|seeking)\b', cleaned)
        if hiring_match:
            company = hiring_match.group(1).strip()
        else:
            at_match = re.search(r'\bat\s+([A-Z][a-zA-Z0-9\s]{1,25})\b', cleaned)
            if at_match and at_match.group(1).lower() not in ["least", "home", "scale", "any"]:
                company = at_match.group(1).strip()
    if not company:
        # Check lines[:4] for header lines with company (e.g. "TechVanguard Inc. - San Francisco, CA")
        for line in lines[:4]:
            if line != title and ('-' in line or '|' in line or ',' in line):
                candidate = re.split(r'[\-|–|—|,]', line)[0].strip()
                if candidate and len(candidate.split()) <= 4 and not any(k in candidate.lower() for k in ["senior", "junior", "lead", "engineer", "developer", "about", "role", "position"]):
                    company = candidate
                    break

    if not company:
        company = "Target Organization"

    # 3. Experience Level Extraction
    exp_level = None
    exp_match = re.search(r'(\d+\+?\s*(?:to\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|professional\s+experience)?)', cleaned, re.IGNORECASE)
    if exp_match:
        exp_level = exp_match.group(0).strip()
    elif "senior" in cleaned.lower():
        exp_level = "5+ years (Senior level)"
    elif "lead" in cleaned.lower() or "staff" in cleaned.lower() or "principal" in cleaned.lower():
        exp_level = "7+ years (Staff/Lead level)"
    elif "junior" in cleaned.lower() or "entry" in cleaned.lower():
        exp_level = "0-2 years (Entry/Junior level)"
    else:
        exp_level = "3+ years professional experience"

    # 4. Required vs Preferred Skills Extraction
    required_skills = []
    preferred_skills = []

    # Segment JD into sections if present
    req_section = ""
    pref_section = ""
    resp_section = ""

    req_match = re.search(r'(?:REQUIREMENTS|REQUIRED\s+SKILLS|MUST\s+HAVE|MINIMUM\s+QUALIFICATIONS|WHAT\s+YOU\s+NEED)[\s:\-]*\n(.*?)(?=(?:NICE\s+TO\s+HAVE|PREFERRED|BONUS|RESPONSIBILITIES|WHAT\s+YOU\'LL\s+DO|BENEFITS|$))', cleaned, re.IGNORECASE | re.DOTALL)
    if req_match:
        req_section = req_match.group(1)

    pref_match = re.search(r'(?:NICE\s+TO\s+HAVE|PREFERRED\s+SKILLS|BONUS|PLUS|ADDITIONAL\s+QUALIFICATIONS)[\s:\-]*\n(.*?)(?=(?:RESPONSIBILITIES|WHAT\s+YOU\'LL\s+DO|BENEFITS|$))', cleaned, re.IGNORECASE | re.DOTALL)
    if pref_match:
        pref_section = pref_match.group(1)

    resp_match = re.search(r'(?:RESPONSIBILITIES|WHAT\s+YOU\'LL\s+DO|THE\s+ROLE|DUTIES)[\s:\-]*\n(.*?)(?=(?:REQUIREMENTS|QUALIFICATIONS|NICE\s+TO\s+HAVE|BENEFITS|$))', cleaned, re.IGNORECASE | re.DOTALL)
    if resp_match:
        resp_section = resp_match.group(1)

    if req_section:
        required_skills = extract_skills_from_text(req_section)
    if pref_section:
        preferred_skills = extract_skills_from_text(pref_section)

    all_extracted_skills = extract_skills_from_text(cleaned)

    # If no separate sections detected, classify top skills as required
    if not required_skills:
        required_skills = all_extracted_skills[:6]
        preferred_skills = all_extracted_skills[6:]
    else:
        # Add remaining skills to preferred if not in required
        for s in all_extracted_skills:
            if s not in required_skills and s not in preferred_skills:
                preferred_skills.append(s)

    # 5. Responsibilities
    responsibilities = []
    source_resp = resp_section if resp_section else cleaned
    for line in source_resp.split("\n"):
        clean_l = line.lstrip('-•*–— ').strip()
        if len(clean_l) > 15 and any(verb in clean_l.lower().split()[:2] for verb in ["design", "build", "lead", "develop", "architect", "collaborate", "maintain", "scale", "implement", "work", "create", "drive", "optimize"]):
            responsibilities.append(clean_l)
            if len(responsibilities) >= 4:
                break

    if not responsibilities:
        responsibilities = [
            f"Design, build, and maintain production-grade software for {title}.",
            "Collaborate with cross-functional teams to define architecture and project specifications.",
            "Optimize system performance, security, reliability, and code quality."
        ]

    # 6. Qualifications
    qualifications = []
    source_qual = req_section if req_section else cleaned
    for line in source_qual.split("\n"):
        clean_l = line.lstrip('-•*–— ').strip()
        if len(clean_l) > 15 and any(k in clean_l.lower() for k in ["bachelor", "master", "degree", "experience", "proficiency", "demonstrated", "knowledge of", "proven track"]):
            qualifications.append(clean_l)
            if len(qualifications) >= 3:
                break

    if not qualifications:
        qualifications = [
            f"{exp_level} in software engineering or related technical field.",
            f"Hands-on proficiency with {', '.join(required_skills[:3]) if required_skills else 'core backend systems'}."
        ]

    return {
        "title": title,
        "company": company,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_level": exp_level,
        "responsibilities": responsibilities,
        "technologies": sorted(list(set(required_skills + preferred_skills))),
        "qualifications": qualifications
    }
