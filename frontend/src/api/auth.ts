import { apiClient } from './client';
import type { AuthResponse, User, RegisterResponse, VerifyEmailResponse, ResendOtpResponse } from '../types';

export const authApi = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/auth/login', { email, password });
    return res.data;
  },

  register: async (name: string, email: string, password: string, target_role?: string): Promise<RegisterResponse> => {
    const res = await apiClient.post<RegisterResponse>('/auth/register', { name, email, password, target_role });
    return res.data;
  },

  verifyEmail: async (email: string, otp: string): Promise<VerifyEmailResponse> => {
    const res = await apiClient.post<VerifyEmailResponse>('/auth/verify-email', { email, otp });
    return res.data;
  },

  resendOtp: async (email: string): Promise<ResendOtpResponse> => {
    const res = await apiClient.post<ResendOtpResponse>('/auth/resend-otp', { email });
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },
};

