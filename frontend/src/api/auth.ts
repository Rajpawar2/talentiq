import { apiClient } from './client';
import type { AuthResponse, User, RegisterResponse } from '../types';

export const authApi = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/auth/login', { email, password });
    return res.data;
  },

  demoLogin: async (): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/auth/demo');
    return res.data;
  },

  register: async (
    name: string,
    email: string,
    password: string,
    target_role?: string,
    confirm_password?: string
  ): Promise<RegisterResponse> => {
    const res = await apiClient.post<RegisterResponse>('/auth/register', {
      name,
      email,
      password,
      confirm_password,
      target_role,
    });
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },
};
