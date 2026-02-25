import apiClient from './client';
import type { AgentResponse } from '../types';

export async function runAgentQuery(query: string): Promise<AgentResponse> {
  const { data } = await apiClient.post('/agent/query', { query });
  return data;
}
