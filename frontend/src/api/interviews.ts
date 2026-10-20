import { apiClient } from './client';
import type { InterviewSession, AnswerResponse, InterviewReport, InterviewQuestion } from '../types';

export const interviewsApi = {
  createInterview: async (data: {
    role: string;
    interview_type: string;
    difficulty: string;
    total_questions: number;
    duration_minutes: number;
    resume_id?: string;
    job_id?: string;
    company?: string;
  }): Promise<InterviewSession> => {
    const res = await apiClient.post<InterviewSession>('/interviews', data);
    return res.data;
  },

  getInterviews: async (): Promise<InterviewSession[]> => {
    const res = await apiClient.get<InterviewSession[]>('/interviews');
    return res.data;
  },

  getInterviewById: async (id: string): Promise<InterviewSession> => {
    const res = await apiClient.get<InterviewSession>(`/interviews/${id}`);
    return res.data;
  },

  startInterview: async (id: string): Promise<InterviewSession> => {
    const res = await apiClient.post<InterviewSession>(`/interviews/${id}/start`);
    return res.data;
  },

  submitAnswer: async (interviewId: string, payload: {
    question_id: string;
    answer_text: string;
    input_mode: 'text' | 'voice';
    audio_duration_seconds?: number;
  }): Promise<AnswerResponse> => {
    const res = await apiClient.post<AnswerResponse>(`/interviews/${interviewId}/answer`, payload);
    return res.data;
  },

  completeInterview: async (id: string): Promise<InterviewSession> => {
    const res = await apiClient.post<InterviewSession>(`/interviews/${id}/complete`);
    return res.data;
  },

  getQuestions: async (interviewId: string): Promise<InterviewQuestion[]> => {
    const res = await apiClient.get<InterviewQuestion[]>(`/interviews/${interviewId}/questions`);
    return res.data;
  },

  getReport: async (interviewId: string): Promise<InterviewReport> => {
    const res = await apiClient.get<InterviewReport>(`/interviews/${interviewId}/report`);
    return res.data;
  },

  transcribeAudio: async (audioBlob: Blob, durationSeconds?: number): Promise<{ transcript: string; duration_seconds: number }> => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    if (durationSeconds) {
      formData.append('duration_seconds', durationSeconds.toString());
    }
    const res = await apiClient.post<{ transcript: string; duration_seconds: number }>('/voice/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
};
