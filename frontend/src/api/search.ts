import apiClient from './client';
import type { SearchResponse } from '../types';

export async function searchFiles(
  query: string,
  limit = 10,
  fileType?: string
): Promise<SearchResponse> {
  const params: Record<string, any> = { q: query, limit };
  if (fileType) params.type = fileType;
  const { data } = await apiClient.get('/search', { params });
  return data;
}
