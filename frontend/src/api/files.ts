import apiClient from './client';
import type { FileListResponse, FileStatsResponse } from '../types';

export async function getFiles(skip = 0, limit = 20, fileType?: string): Promise<FileListResponse> {
  const params: Record<string, any> = { skip, limit };
  if (fileType) params.file_type = fileType;
  const { data } = await apiClient.get('/files', { params });
  return data;
}

export async function getFileStats(): Promise<FileStatsResponse> {
  const { data } = await apiClient.get('/files/stats');
  return data;
}

export async function getFileContent(fileId: string): Promise<{ content: string; chunk_count: number }> {
  const { data } = await apiClient.get(`/files/${fileId}/content`);
  return data;
}
