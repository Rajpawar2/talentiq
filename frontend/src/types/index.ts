export type User = {
  id: string;
  name: string;
  email: string;
  target_role?: string;
  email_verified?: boolean;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type RegisterResponse = {
  success: boolean;
  message: string;
  email: string;
};

export type VerifyEmailResponse = {
  success: boolean;
  message: string;
};

export type ResendOtpResponse = {
  success: boolean;
  message: string;
  cooldown_seconds?: number;
};

export type ResumeData = {
  id: string;
  user_id: string;
  filename: string;
  skills: string[];
  parsed_data: {
    name?: string;
    email?: string;
    phone?: string;
    summary?: string;
    education?: Array<{ degree: string; institution: string; year: string; gpa?: string }>;
    experience?: Array<{ role: string; company: string; duration: string; highlights: string[] }>;
    projects?: Array<{ name: string; tech: string[]; description: string }>;
    certifications?: string[];
    achievements?: string[];
  };
  created_at: string;
  updated_at: string;
};

export type ResumeListItem = {
  id: string;
  filename: string;
  skills_count: number;
  top_skills: string[];
  created_at: string;
};

export type JobDescriptionData = {
  id: string;
  user_id: string;
  title: string;
  company?: string;
  raw_text: string;
  parsed_data: {
    title: string;
    company?: string;
    required_skills: string[];
    preferred_skills: string[];
    experience_level?: string;
    responsibilities: string[];
    technologies: string[];
    qualifications: string[];
  };
  created_at: string;
};

export type MatchingResult = {
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  experience_match: string;
  strengths: string[];
  recommendations: string[];
  skill_match_percentage: number;
  semantic_similarity: number;
};

export type InterviewQuestion = {
  id: string;
  question_index: number;
  question_text: string;
  category: string;
  difficulty_level: string;
  is_follow_up: boolean;
  follow_up_reason?: string;
};

export type InterviewSession = {
  id: string;
  title: string;
  role: string;
  company?: string;
  interview_type: 'Technical' | 'Behavioral' | 'Mixed' | 'Coding';
  difficulty: 'Easy' | 'Medium' | 'Hard';
  total_questions: number;
  duration_minutes: number;
  status: 'created' | 'in_progress' | 'completed' | 'abandoned';
  current_question_index: number;
  overall_score?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  questions?: InterviewQuestion[];
  current_question?: InterviewQuestion;
};

export type CommunicationIndicators = {
  clarity_indicator: number;
  conciseness_indicator: number;
  structure_indicator: number;
  vocabulary_indicator: number;
  pacing_assessment: string;
  observations: string;
};

export type AnswerResponse = {
  id: string;
  question_id: string;
  answer_text: string;
  input_mode: 'text' | 'voice';
  filler_words_count: number;
  filler_breakdown: Record<string, number>;
  filler_frequency_pct: number;
  words_count: number;
  speech_pace_wpm?: number;
  communication_indicators: CommunicationIndicators;
};

export type QuestionReviewItem = {
  question_id: string;
  question_index: number;
  question_text: string;
  category: string;
  difficulty_level: string;
  is_follow_up: boolean;
  candidate_answer?: string;
  input_mode?: string;
  evaluation?: {
    id: string;
    technical_accuracy: number;
    relevance: number;
    completeness: number;
    clarity: number;
    problem_solving: number;
    overall_score: number;
    strengths: string[];
    weaknesses: string[];
    feedback?: string;
    ideal_answer?: string;
    next_difficulty_adjustment: string;
    recommended_follow_up?: string;
  };
  filler_count?: number;
  filler_breakdown?: Record<string, number>;
};

export type InterviewReport = {
  interview_id: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
  behavioral_score: number;
  resume_match_score: number;
  interview_readiness: 'High' | 'Moderate' | 'Needs Preparation';
  key_strengths: string[];
  weak_areas: string[];
  recommended_topics: string[];
  prep_plan: string[];
  detailed_summary: string;
  total_questions: number;
  answered_questions: number;
  question_reviews: QuestionReviewItem[];
  created_at: string;
};

export type ScoreTrendItem = {
  interview_id: string;
  date: string;
  role: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
};

export type AnalyticsOverview = {
  total_interviews: number;
  average_score: number;
  best_score: number;
  resume_match_score: number;
  technical_score: number;
  communication_score: number;
  recent_interviews: Array<{
    id: string;
    title: string;
    role: string;
    type: string;
    status: string;
    score: number;
    created_at: string;
  }>;
  performance_trend: ScoreTrendItem[];
  skill_strengths: Array<{ skill: string; level: number; status: string }>;
  skill_gaps: Array<{ skill: string; level: number; priority: string }>;
  recommended_practice: string[];
};

export type AnalyticsProgress = {
  score_over_time: ScoreTrendItem[];
  category_averages: Record<string, number>;
  skill_radar: Array<{ subject: string; score: number; benchmark: number }>;
  improvement_insights: string[];
};
