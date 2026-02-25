import apiClient from './client';

export async function ingestFile(filePath: string) {
  const { data } = await apiClient.post('/ingest', { file_path: filePath });
  return data;
}

export async function ingestDirectory(directoryPath: string) {
  const { data } = await apiClient.post('/ingest/directory', { directory_path: directoryPath });
  return data;
}

export async function deleteIndexedFile(fileId: string) {
  const { data } = await apiClient.delete(`/ingest/${fileId}`);
  return data;
}
