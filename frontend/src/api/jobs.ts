import { apiClient } from './client';
import type { JobDescriptionData, MatchingResult } from '../types';

export const jobsApi = {
  createJob: async (title: string, raw_text: string, company?: string): Promise<JobDescriptionData> => {
    const res = await apiClient.post<JobDescriptionData>('/jobs', { title, raw_text, company });
    return res.data;
  },

  uploadJobFile: async (file: File): Promise<JobDescriptionData> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<JobDescriptionData>('/jobs/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  getJobs: async (): Promise<JobDescriptionData[]> => {
    const res = await apiClient.get<JobDescriptionData[]>('/jobs');
    return res.data;
  },

  getJobById: async (id: string): Promise<JobDescriptionData> => {
    const res = await apiClient.get<JobDescriptionData>(`/jobs/${id}`);
    return res.data;
  },

  analyzeMatch: async (payload: { resume_id?: string; job_id?: string; resume_text?: string; job_text?: string }): Promise<MatchingResult> => {
    const res = await apiClient.post<MatchingResult>('/matching/analyze', payload);
    return res.data;
  },
};
