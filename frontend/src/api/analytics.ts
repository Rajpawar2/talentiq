import { apiClient } from './client';
import type { AnalyticsOverview, AnalyticsProgress } from '../types';

export const analyticsApi = {
  getOverview: async (): Promise<AnalyticsOverview> => {
    const res = await apiClient.get<AnalyticsOverview>('/analytics/overview');
    return res.data;
  },

  getProgress: async (): Promise<AnalyticsProgress> => {
    const res = await apiClient.get<AnalyticsProgress>('/analytics/progress');
    return res.data;
  },
};
