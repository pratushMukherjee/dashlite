export interface FileRecord {
  id: string;
  file_path: string;
  file_name: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: string;
  error_message?: string | null;
  created_at: string;
  indexed_at?: string | null;
}

export interface FileListResponse {
  files: FileRecord[];
  total: number;
}

export interface FileStatsResponse {
  total_files: number;
  total_chunks: number;
  files_by_type: Record<string, number>;
  total_size_bytes: number;
}

export interface SearchResult {
  chunk_id: string;
  file_id: string;
  file_name: string;
  file_type: string;
  text: string;
  score: number;
  chunk_index: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total: number;
  latency_ms: number;
}

export interface SourceCitation {
  file_id: string;
  file_name: string;
  chunk_text: string;
  relevance_score: number;
}

export interface AskResponse {
  answer: string;
  sources: SourceCitation[];
  question: string;
  latency_ms: number;
}

export interface AgentStep {
  step_type: string;
  tool?: string | null;
  description: string;
  detail: string;
  duration_ms: number;
}

export interface AgentResponse {
  query: string;
  steps: AgentStep[];
  answer: string;
  latency_ms: number;
}

export interface ActivityEvent {
  id: number;
  event_type: string;
  file_id?: string | null;
  detail?: string | null;
  created_at: string;
}

export interface ActivityFeedResponse {
  events: ActivityEvent[];
  total: number;
}

export interface ActivityStatsResponse {
  total_files: number;
  total_queries: number;
  queries_today: number;
  files_by_type: Record<string, number>;
}
