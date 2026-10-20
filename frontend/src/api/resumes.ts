import { apiClient } from './client';
import type { ResumeData, ResumeListItem } from '../types';

export const resumesApi = {
  uploadResume: async (file: File): Promise<ResumeData> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<ResumeData>('/resumes/upload', formData);
    return res.data;
  },

  getResumes: async (): Promise<ResumeListItem[]> => {
    const res = await apiClient.get<ResumeListItem[]>('/resumes');
    return res.data;
  },

  getResumeById: async (id: string): Promise<ResumeData> => {
    const res = await apiClient.get<ResumeData>(`/resumes/${id}`);
    return res.data;
  },
};
