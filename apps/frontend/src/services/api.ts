import axios from 'axios';

export type ProcessingStrategy = 'parser' | 'scanner_ocr' | 'ocr_model';

export interface SearchSnippet {
  chunk_id: string;
  phrase: string;
  page_number?: number | null;
  heading_path: string[];
}

export interface SearchResult {
  document_id: string;
  title: string;
  url: string;
  score: number;
  snippets: SearchSnippet[];
}

export interface SearchResponse {
  items: SearchResult[];
}

export interface DocumentListItem {
  id: string;
  title: string;
  original_filename: string;
  mime_type: string;
  status: string;
  processing_strategy: ProcessingStrategy;
}

export function getOriginalDocumentUrl(documentId: string): string {
  return `/api/documents/${documentId}/original`;
}

export const api = axios.create({
  baseURL: '/api',
});

export async function searchDocuments(query: string): Promise<SearchResponse> {
  const response = await api.post<SearchResponse>('/search', { query, limit: 10 });
  return response.data;
}

export async function uploadDocument(file: File, strategy: ProcessingStrategy) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('strategy', strategy);

  const response = await api.post('/documents', formData);
  return response.data;
}

export async function listDocuments(): Promise<DocumentListItem[]> {
  const response = await api.get<DocumentListItem[]>('/documents');
  return response.data;
}

export async function getDocumentMarkdown(documentId: string): Promise<string> {
  const response = await api.get<string>(`/documents/${documentId}/markdown`);
  return response.data;
}

