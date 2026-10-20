import hashlib
import re
from typing import List, Dict, Any, Optional
from app.ai.base import AIProvider

class MockAIProvider(AIProvider):
    """
    High-fidelity deterministic Mock AI Provider.
    Enables fully functional, zero-cost local execution without external API keys.
    Grounds questions and evaluations in candidate inputs.
    """

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
        # Detect relevant skills from resume and job description to personalize
        combined_text = f"{role} {resume_text or ''} {job_text or ''}".lower()
        
        detected_tech = []
        tech_keywords = [
            "python", "fastapi", "react", "typescript", "docker", "kubernetes",
            "postgresql", "redis", "aws", "graphql", "system design", "microservices",
            "ci/cd", "node.js", "django", "machine learning", "pytorch", "rest api"
        ]
        for tech in tech_keywords:
            if tech in combined_text:
                detected_tech.append(tech.title())
        
        if not detected_tech:
            detected_tech = ["System Architecture", "REST APIs", "Database Optimization", "State Management"]

        company_str = f" at {company}" if company else ""
        
        # Curated library of contextual questions
        library = [
            {
                "question_text": f"Walk me through an end-to-end project where you utilized {detected_tech[0] if len(detected_tech) > 0 else 'backend services'}. What architecture decisions did you make and what trade-offs did you consider?",
                "category": "Project-based",
                "difficulty_level": difficulty,
                "expected_key_points": [
                    "Clear architectural overview and rationale",
                    "Explicit trade-offs between speed, cost, and maintainability",
                    "Measurable impact or performance metrics"
                ]
            },
            {
                "question_text": f"In {detected_tech[1] if len(detected_tech) > 1 else detected_tech[0]}, how do you handle concurrency, asynchronous operations, and fault tolerance under high throughput?",
                "category": "Technical",
                "difficulty_level": difficulty,
                "expected_key_points": [
                    "Event loop / thread pool mechanics",
                    "Connection pooling and backpressure strategies",
                    "Graceful degradation and circuit breakers"
                ]
            },
            {
                "question_text": f"Describe a critical production incident or challenging bug you resolved. How did you isolate root cause and prevent regression?",
                "category": "Problem-solving",
                "difficulty_level": difficulty,
                "expected_key_points": [
                    "Structured diagnostic methodology (logs, traces, metrics)",
                    "Root cause identification vs surface patching",
                    "Post-mortem action items and automated safeguards"
                ]
            },
            {
                "question_text": f"Tell me about a time you had a strong technical disagreement with a team member or stakeholder{company_str}. How did you align on a path forward?",
                "category": "Behavioral",
                "difficulty_level": "Medium",
                "expected_key_points": [
                    "Empathy and active listening",
                    "Objective data/benchmarking over subjective opinions",
                    "Commitment to team velocity and cohesion"
                ]
            },
            {
                "question_text": f"How do you approach database schema design, index tuning, and query optimization when scaling read/write workloads?",
                "category": "Technical",
                "difficulty_level": difficulty,
                "expected_key_points": [
                    "Indexing strategies (B-Tree, partial indexes)",
                    "Query execution plan analysis (EXPLAIN ANALYZE)",
                    "Read replicas and caching tiers (Redis)"
                ]
            },
            {
                "question_text": f"When building client-facing applications in {role}, how do you ensure accessibility (WCAG), resilience against network failures, and optimal rendering performance?",
                "category": "Role-specific",
                "difficulty_level": difficulty,
                "expected_key_points": [
                    "Semantic markup and keyboard navigability",
                    "Optimistic UI updates and offline caching",
                    "Core Web Vitals and render tree efficiency"
                ]
            },
            {
                "question_text": "If you had to redesign a legacy monolithic system into modular services without downtime, what deployment and migration strategy would you employ?",
                "category": "Technical",
                "difficulty_level": "Hard",
                "expected_key_points": [
                    "Strangler Fig pattern",
                    "Dual-write and dual-read validation phases",
                    "Automated rollback and zero-downtime routing"
                ]
            }
        ]

        # Select requested number of questions
        selected = []
        for i in range(num_questions):
            template = library[i % len(library)].copy()
            template["question_index"] = i + 1
            template["is_follow_up"] = False
            template["follow_up_reason"] = None
            selected.append(template)

        return selected

    def evaluate_answer(
        self,
        question_text: str,
        category: str,
        difficulty: str,
        answer_text: str,
        expected_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        words = answer_text.strip().split()
        word_count = len(words)
        
        # Meaningful heuristic scoring based on depth, domain vocabulary, structure
        has_technical_keywords = any(k in answer_text.lower() for k in [
            "async", "await", "cache", "latency", "scale", "database", "index", "api",
            "service", "test", "metric", "architecture", "tradeoff", "user", "performance"
        ])
        
        has_star_structure = any(s in answer_text.lower() for s in [
            "situation", "task", "action", "result", "because", "impact", "we achieved", "improved"
        ])

        # Baseline evaluation metrics
        if word_count < 15:
            tech = 4.0
            relevance = 5.0
            completeness = 3.5
            clarity = 5.0
            problem_solving = 4.0
            strengths = ["Direct response initiation"]
            weaknesses = ["Answer lacks substantive depth and detail", "No concrete examples or metrics provided"]
            feedback = "Your answer was quite brief. Elaborate further by detailing the exact technical mechanism and real-world results."
            adjustment = "decrease"
        elif word_count < 45:
            tech = 6.8 if has_technical_keywords else 6.0
            relevance = 7.5
            completeness = 6.2
            clarity = 7.2
            problem_solving = 6.5
            strengths = ["Clear conceptual grasp", "Addressed the primary intent of the question"]
            weaknesses = ["Could include more specific architectural nuances and metric outcomes"]
            feedback = "Solid answer! To elevate this to staff level, incorporate quantitative outcomes (e.g. latency reduced by 40%) and edge-case handling."
            adjustment = "maintain"
        else:
            tech = 8.8 if has_technical_keywords else 8.0
            relevance = 9.0
            completeness = 8.5
            clarity = 8.6
            problem_solving = 8.4 if has_star_structure else 8.0
            strengths = [
                "Comprehensive explanation with structured reasoning",
                "Strong use of domain terminology and architectural clarity",
                "Demonstrated thoughtful trade-off analysis"
            ]
            weaknesses = ["Ensure you keep pacing concise to avoid diluting the core takeaway"]
            feedback = "Excellent response! You demonstrated strong technical ownership, structured reasoning, and a clear understanding of practical implementation constraints."
            adjustment = "increase"

        overall = round((tech * 0.35 + relevance * 0.25 + completeness * 0.15 + clarity * 0.15 + problem_solving * 0.10), 1)

        ideal = (
            f"An exemplary response outlines: 1) The specific problem context and requirements; "
            f"2) Core architectural decision with specific tools (e.g., connection pools, indexing, caching); "
            f"3) Concrete trade-offs evaluated; and 4) Measured production outcomes (reliability, latency, developer velocity)."
        )

        return {
            "technical_accuracy": tech,
            "relevance": relevance,
            "completeness": completeness,
            "clarity": clarity,
            "problem_solving": problem_solving,
            "overall_score": overall,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback": feedback,
            "ideal_answer": ideal,
            "next_difficulty_adjustment": adjustment,
            "recommended_follow_up": f"Could you elaborate on how you monitored and verified the operational reliability of that solution?"
        }

    def generate_followup(
        self,
        previous_question: str,
        candidate_answer: str,
        evaluation: Dict[str, Any],
        target_role: str,
        remaining_questions: int
    ) -> Dict[str, Any]:
        """
        Adaptive Engine: Dynamically changes difficulty or creates a targeted drill-down.
        """
        score = evaluation.get("overall_score", 7.0)
        adjustment = evaluation.get("next_difficulty_adjustment", "maintain")
        
        if score < 5.5:
            # Candidate struggled: simplify or ask a foundational conceptual question
            return {
                "question_text": f"Let's break that down into fundamentals: What core principles or metrics would you check first when debugging that system behavior?",
                "category": "Technical",
                "difficulty_level": "Easy",
                "is_follow_up": True,
                "follow_up_reason": "Candidate's prior answer lacked foundational depth; probing core principles.",
                "expected_key_points": ["First-principles debugging", "Observability metrics", "Basic isolation steps"]
            }
        elif score >= 8.0:
            # Candidate excelled: advance difficulty with edge cases and distributed scale
            return {
                "question_text": f"That's a strong solution. Now suppose traffic spikes by 50x and nodes start experiencing network partitions: how would your design guarantee data consistency and availability?",
                "category": "Technical",
                "difficulty_level": "Hard",
                "is_follow_up": True,
                "follow_up_reason": "Candidate gave a high-scoring answer; dynamically elevating to distributed scale and fault tolerance.",
                "expected_key_points": ["CAP theorem trade-offs", "Idempotency keys", "Distributed locks vs eventual consistency"]
            }
        else:
            # Candidate gave a solid baseline answer: probe for edge cases or practical tradeoffs
            return {
                "question_text": f"Interesting approach. What was the most significant edge case or failure mode you encountered with that pattern, and how did you mitigate it?",
                "category": "Problem-solving",
                "difficulty_level": "Medium",
                "is_follow_up": True,
                "follow_up_reason": "Candidate demonstrated solid baseline knowledge; exploring practical edge-case mitigation.",
                "expected_key_points": ["Edge-case identification", "Defensive validation", "Monitoring and alerting"]
            }

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Extracts structured entities, skills, education, and experiences."""
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
        
        # Email & Phone regex
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
        email = email_match.group(0) if email_match else "candidate@example.com"
        
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)
        phone = phone_match.group(0) if phone_match else "+1 (555) 019-2834"
        
        name = lines[0] if lines else "Alex Morgan"
        if len(name.split()) > 4 or "@" in name:
            name = "Alex Morgan"

        # Known skills scanning
        skill_catalog = [
            "Python", "FastAPI", "React", "TypeScript", "JavaScript", "Docker", "Kubernetes",
            "PostgreSQL", "SQL", "Redis", "AWS", "GCP", "CI/CD", "Git", "System Design",
            "REST APIs", "GraphQL", "Tailwind CSS", "Next.js", "Node.js", "Microservices",
            "PyTorch", "TensorFlow", "Pandas", "Scikit-Learn", "HTML5", "CSS3", "Linux"
        ]
        
        matched_skills = []
        lower_text = resume_text.lower()
        for skill in skill_catalog:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', lower_text):
                matched_skills.append(skill)
        
        if not matched_skills:
            matched_skills = ["Python", "FastAPI", "PostgreSQL", "REST APIs", "Docker", "Git"]

        # Parse experience blocks
        experience = [
            {
                "role": "Senior Software Engineer",
                "company": "NextGen Systems",
                "duration": "2022 - Present",
                "highlights": [
                    "Architected high-throughput microservices processing 10M+ daily events",
                    "Reduced p99 API latency from 450ms to 85ms via Redis caching and query indexing",
                    "Led cross-functional team of 6 engineers across product releases"
                ]
            },
            {
                "role": "Software Engineer",
                "company": "CloudScale Labs",
                "duration": "2020 - 2022",
                "highlights": [
                    "Developed asynchronous REST APIs using FastAPI and PostgreSQL",
                    "Configured CI/CD deployment pipelines on Docker and Kubernetes"
                ]
            }
        ]

        education = [
            {
                "degree": "B.S. in Computer Science",
                "institution": "State University of Technology",
                "year": "2020",
                "gpa": "3.8 / 4.0"
            }
        ]

        projects = [
            {
                "name": "Distributed Task Scheduler",
                "tech": ["Python", "Redis", "FastAPI"],
                "description": "Fault-tolerant background task orchestration engine with retry policies and priority queues."
            },
            {
                "name": "Real-time Telemetry Dashboard",
                "tech": ["React", "TypeScript", "WebSocket"],
                "description": "High-frequency streaming data visualization platform with interactive charts."
            }
        ]

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": matched_skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": ["AWS Certified Solutions Architect", "CKA: Certified Kubernetes Administrator"],
            "achievements": ["Hackathon Winner (1st Place, 2023)", "Open Source Contributor"],
            "summary": f"Experienced software engineer proficient in {', '.join(matched_skills[:4])} with a proven track record of architecting scalable distributed systems and delivering reliable user-focused products."
        }

    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Analyzes job description requirements and qualifications."""
        lower_text = jd_text.lower()
        
        # Skill extraction
        skill_catalog = [
            "Python", "FastAPI", "React", "TypeScript", "Docker", "Kubernetes",
            "PostgreSQL", "Redis", "AWS", "CI/CD", "System Design", "Microservices",
            "GraphQL", "REST APIs", "Kafka", "Golang", "Java", "Terraform"
        ]
        
        required_skills = []
        for s in skill_catalog:
            if s.lower() in lower_text:
                required_skills.append(s)
                
        if not required_skills:
            required_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "System Design"]

        return {
            "title": "Senior AI / Full-Stack Engineer",
            "company": "Innovate AI",
            "required_skills": required_skills[:5],
            "preferred_skills": required_skills[5:] if len(required_skills) > 5 else ["Kubernetes", "Redis", "Kafka"],
            "experience_level": "3+ years professional software development",
            "responsibilities": [
                "Design and maintain scalable backend microservices and modern web interfaces",
                "Collaborate with product and AI researchers to ship production AI features",
                "Conduct code reviews, mentor junior teammates, and uphold engineering excellence"
            ],
            "technologies": required_skills,
            "qualifications": [
                "Bachelor's or equivalent experience in Computer Science or related field",
                "Demonstrated proficiency in asynchronous programming and modern databases"
            ]
        }

    def generate_report(
        self,
        interview_data: Dict[str, Any],
        answers_and_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates comprehensive final assessment report."""
        if not answers_and_evaluations:
            return {
                "overall_score": 75.0,
                "technical_score": 76.0,
                "communication_score": 74.0,
                "problem_solving_score": 75.0,
                "behavioral_score": 75.0,
                "resume_match_score": 82.0,
                "interview_readiness": "Moderate",
                "key_strengths": ["Clear communication", "Structured approach"],
                "weak_areas": ["Needs more deep-dive examples"],
                "recommended_topics": ["Distributed Systems", "Database Indexing"],
                "prep_plan": ["Practice system design trade-offs", "Implement mock concurrency tests"],
                "detailed_summary": "Candidate demonstrated capable baseline competency with growth opportunity in high-scale architectural specifics."
            }

        scores = [item.get("evaluation", {}).get("overall_score", 7.0) for item in answers_and_evaluations if item.get("evaluation")]
        avg_score = sum(scores) / len(scores) if scores else 7.2
        scaled_overall = round(avg_score * 10, 1)

        tech_scores = [item.get("evaluation", {}).get("technical_accuracy", 7.0) * 10 for item in answers_and_evaluations if item.get("evaluation")]
        tech_avg = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 78.0

        clarity_scores = [item.get("evaluation", {}).get("clarity", 7.0) * 10 for item in answers_and_evaluations if item.get("evaluation")]
        comm_avg = round(sum(clarity_scores) / len(clarity_scores), 1) if clarity_scores else 75.0

        ps_scores = [item.get("evaluation", {}).get("problem_solving", 7.0) * 10 for item in answers_and_evaluations if item.get("evaluation")]
        ps_avg = round(sum(ps_scores) / len(ps_scores), 1) if ps_scores else 76.0

        behavioral_avg = round((comm_avg + ps_avg) / 2, 1)

        readiness = "High" if scaled_overall >= 80 else ("Moderate" if scaled_overall >= 65 else "Needs Preparation")

        role = interview_data.get("role", "Software Engineer")
        
        return {
            "overall_score": scaled_overall,
            "technical_score": tech_avg,
            "communication_score": comm_avg,
            "problem_solving_score": ps_avg,
            "behavioral_score": behavioral_avg,
            "resume_match_score": 85.0,
            "interview_readiness": readiness,
            "key_strengths": [
                f"Strong conceptual understanding of {role} fundamentals",
                "Structured reasoning with logical problem breakdown",
                "Good self-awareness and practical design orientation"
            ],
            "weak_areas": [
                "Could quantify production metrics more consistently (e.g. throughput, p99 latency)",
                "Pacing in initial answers could be streamlined to reach core conclusions faster"
            ],
            "recommended_topics": [
                "Distributed consistency models and CAP trade-offs",
                "Database lock contention and indexing optimization",
                "STAR method storytelling for behavioral questions"
            ],
            "prep_plan": [
                "Review high-availability architectural patterns and caching strategies",
                "Conduct 2-3 timed mock sessions focusing on conciseness within 90 seconds per answer",
                "Prepare 3 concrete STAR stories highlighting measurable technical ownership"
            ],
            "detailed_summary": (
                f"Overall, the candidate showcased strong potential for the {role} position. "
                f"They achieved an overall interview index of {scaled_overall}/100, demonstrating a firm grasp of core competencies, "
                f"effective problem decomposition, and clear communication. Addressing the identified weak areas in system scaling "
                f"metrics will make their candidacy exceptionally competitive."
            )
        }

    def generate_embedding(self, text: str) -> List[float]:
        """Generates deterministic pseudo-dense vector based on SHA-256 hash."""
        vector = []
        for i in range(16):
            h = hashlib.sha256(f"{text}_{i}".encode('utf-8')).hexdigest()
            # Normalize to [-1.0, 1.0]
            val = (int(h[:4], 16) / 65535.0) * 2.0 - 1.0
            vector.append(round(val, 4))
        return vector
