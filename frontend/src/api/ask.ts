import apiClient from './client';
import type { AskResponse } from '../types';

export async function askQuestion(question: string, maxSources = 5): Promise<AskResponse> {
  const { data } = await apiClient.post('/ask', { question, max_sources: maxSources });
  return data;
}
