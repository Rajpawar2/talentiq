from typing import Dict, Any
from app.ai.factory import get_ai_provider
from app.services.resume_parser import clean_extracted_text

def parse_job_description_content(jd_text: str) -> Dict[str, Any]:
    """
    Cleans raw job description text and extracts structured requirements using AI provider.
    """
    cleaned = clean_extracted_text(jd_text)
    if not cleaned or len(cleaned) < 15:
        raise ValueError("Job description is too brief. Please provide a more detailed job posting.")

    ai_provider = get_ai_provider()
    return ai_provider.analyze_job_description(cleaned)
