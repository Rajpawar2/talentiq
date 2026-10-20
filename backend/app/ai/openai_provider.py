import json
import httpx
from typing import List, Dict, Any, Optional
from app.ai.base import AIProvider
from app.ai.mock_provider import MockAIProvider
from app.config import settings

class OpenAIProvider(AIProvider):
    """
    OpenAI API Provider implementation with automatic graceful fallback
    to MockAIProvider if keys are absent or HTTP request fails.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL
        self.mock_fallback = MockAIProvider()

    def _call_llm(self, prompt: str, system_message: str = "You are an expert technical interviewer and hiring director.") -> Optional[str]:
        if not self.api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            }
            with httpx.Client(timeout=30.0) as client:
                res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                return None
        except Exception:
            return None

    def generate_questions(
        self,
        role: str,
        interview_type: str,
        difficulty: str,
        num_questions: int,
        resume_text: Optional[str] = None,
        job_text: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        prompt = f"""
        Generate {num_questions} realistic {difficulty}-level interview questions for a {role} ({interview_type} interview).
        Candidate Resume Context: {resume_text[:1500] if resume_text else 'None provided'}
        Job Description Context: {job_text[:1500] if job_text else 'None provided'}
        Company Context: {company or 'None'}

        Return JSON matching this format:
        {{
          "questions": [
             {{
                "question_index": 1,
                "question_text": "...",
                "category": "Technical",
                "difficulty_level": "{difficulty}",
                "expected_key_points": ["point 1", "point 2"],
                "is_follow_up": false,
                "follow_up_reason": null
             }}
          ]
        }}
        """
        response_text = self._call_llm(prompt)
        if response_text:
            try:
                parsed = json.loads(response_text)
                if "questions" in parsed and len(parsed["questions"]) > 0:
                    return parsed["questions"]
            except Exception:
                pass
        
        # Fallback to high-quality mock generator
        return self.mock_fallback.generate_questions(
            role, interview_type, difficulty, num_questions, resume_text, job_text, company
        )

    def evaluate_answer(
        self,
        question_text: str,
        category: str,
        difficulty: str,
        answer_text: str,
        expected_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        prompt = f"""
        Evaluate candidate's answer for this interview question:
        Question: "{question_text}"
        Category: {category}
        Difficulty: {difficulty}
        Candidate Answer: "{answer_text}"
        Expected Key Points: {json.dumps(expected_points or [])}

        Return JSON matching this exact structure:
        {{
          "technical_accuracy": 8.5,
          "relevance": 9.0,
          "completeness": 8.0,
          "clarity": 8.5,
          "problem_solving": 8.0,
          "overall_score": 8.4,
          "strengths": ["string", "string"],
          "weaknesses": ["string"],
          "feedback": "Constructive actionable feedback",
          "ideal_answer": "Model answer",
          "next_difficulty_adjustment": "increase",
          "recommended_follow_up": "Adaptive follow-up question text"
        }}
        """
        response_text = self._call_llm(prompt)
        if response_text:
            try:
                parsed = json.loads(response_text)
                if "overall_score" in parsed:
                    return parsed
            except Exception:
                pass

        return self.mock_fallback.evaluate_answer(
            question_text, category, difficulty, answer_text, expected_points
        )

    def generate_followup(
        self,
        previous_question: str,
        candidate_answer: str,
        evaluation: Dict[str, Any],
        target_role: str,
        remaining_questions: int
    ) -> Dict[str, Any]:
        prompt = f"""
        Act as an adaptive interview engine.
        Target Role: {target_role}
        Prior Question: "{previous_question}"
        Prior Answer: "{candidate_answer}"
        Evaluation: {json.dumps(evaluation)}
        Remaining Questions in Interview: {remaining_questions}

        Decide whether to drill deeper (follow-up on weakness), increase difficulty (reward mastery), or transition topic.
        Return JSON format:
        {{
           "question_text": "...",
           "category": "Technical",
           "difficulty_level": "Hard",
           "is_follow_up": true,
           "follow_up_reason": "Rationale for this adaptation",
           "expected_key_points": ["point 1", "point 2"]
        }}
        """
        response_text = self._call_llm(prompt)
        if response_text:
            try:
                parsed = json.loads(response_text)
                if "question_text" in parsed:
                    return parsed
            except Exception:
                pass

        return self.mock_fallback.generate_followup(
            previous_question, candidate_answer, evaluation, target_role, remaining_questions
        )

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        prompt = f"""
        Extract structured profile data from this resume text:
        Resume Text:
        {resume_text[:4000]}

        Return JSON format:
        {{
          "name": "Full Name",
          "email": "email@example.com",
          "phone": "+1 ...",
          "skills": ["Skill1", "Skill2"],
          "education": [{{"degree": "...", "institution": "...", "year": "..."}}],
          "experience": [{{"role": "...", "company": "...", "duration": "...", "highlights": ["..."]}}],
          "projects": [{{"name": "...", "tech": ["..."], "description": "..."}}],
          "certifications": ["..."],
          "achievements": ["..."],
          "summary": "Brief executive summary"
        }}
        """
        response_text = self._call_llm(prompt)
        if response_text:
            try:
                parsed = json.loads(response_text)
                if "skills" in parsed:
                    return parsed
            except Exception:
                pass

        return self.mock_fallback.analyze_resume(resume_text)

    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        prompt = f"""
        Extract requirements and competencies from this Job Description:
        Job Description Text:
        {jd_text[:4000]}

        Return JSON format:
        {{
          "title": "Job Title",
          "company": "Company Name",
          "required_skills": ["Skill1", "Skill2"],
          "preferred_skills": ["Skill3"],
          "experience_level": "Years/Level",
          "responsibilities": ["Resp1", "Resp2"],
          "technologies": ["Tech1", "Tech2"],
          "qualifications": ["Qual1"]
        }}
        """
        response_text = self._call_llm(prompt)
        if response_text:
            try:
                parsed = json.loads(response_text)
                if "required_skills" in parsed:
                    return parsed
            except Exception:
                pass

        return self.mock_fallback.analyze_job_description(jd_text)

    def generate_report(
        self,
        interview_data: Dict[str, Any],
        answers_and_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        prompt = f"""
        Generate final comprehensive interview report:
        Interview Data: {json.dumps(interview_data)}
        Performance History: {json.dumps(answers_and_evaluations)}

        Return JSON format:
        {{
          "overall_score": 85.0,
          "technical_score": 88.0,
          "communication_score": 82.0,
          "problem_solving_score": 84.0,
          "behavioral_score": 80.0,
          "resume_match_score": 86.0,
          "interview_readiness": "High",
          "key_strengths": ["...", "..."],
          "weak_areas": ["..."],
          "recommended_topics": ["..."],
          "prep_plan": ["..."],
          "detailed_summary": "Comprehensive summary paragraph"
        }}
        """
        response_text = self._call_llm(prompt)
        if response_text:
            try:
                parsed = json.loads(response_text)
                if "overall_score" in parsed:
                    return parsed
            except Exception:
                pass

        return self.mock_fallback.generate_report(interview_data, answers_and_evaluations)

    def generate_embedding(self, text: str) -> List[float]:
        if not self.api_key:
            return self.mock_fallback.generate_embedding(text)

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "text-embedding-3-small",
                "input": text[:8000]
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["data"][0]["embedding"]
        except Exception:
            pass

        return self.mock_fallback.generate_embedding(text)
