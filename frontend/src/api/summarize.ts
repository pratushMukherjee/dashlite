import apiClient from './client';

export async function summarizeFile(fileId: string) {
  const { data } = await apiClient.post(`/summarize/${fileId}`);
  return data;
}
