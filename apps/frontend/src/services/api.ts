import axios, { type AxiosProgressEvent } from 'axios';

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

export interface DocumentUploadResponse {
  document_id: string;
  job_id: string;
  status: string;
  deduplicated: boolean;
}

export function getOriginalDocumentUrl(documentId: string): string {
  return `/api/documents/${documentId}/original`;
}

export function getRecognizedDocumentUrl(documentId: string): string {
  return `/api/documents/${documentId}/recognized`;
}

export function getRecognizedFilename(filename: string): string {
  const dotIndex = filename.lastIndexOf('.');
  const stem = dotIndex > 0 ? filename.slice(0, dotIndex) : filename;
  return `${stem || 'document'}.recognized.md`;
}

export const api = axios.create({
  baseURL: '/api',
});

export async function searchDocuments(query: string): Promise<SearchResponse> {
  const response = await api.post<SearchResponse>('/search', { query, limit: 10 });
  return response.data;
}

export async function uploadDocument(
  file: File,
  strategy: ProcessingStrategy,
  onProgress?: (progress: number) => void,
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('strategy', strategy);

  const response = await api.post<DocumentUploadResponse>('/documents', formData, {
    onUploadProgress: (event: AxiosProgressEvent) => {
      if (!event.total) {
        return;
      }

      onProgress?.(Math.round((event.loaded / event.total) * 100));
    },
  });
  return response.data;
}

export async function listDocuments(): Promise<DocumentListItem[]> {
  const response = await api.get<DocumentListItem[]>('/documents');
  return response.data;
}

export async function getDocument(documentId: string): Promise<DocumentListItem> {
  const response = await api.get<DocumentListItem>(`/documents/${documentId}`);
  return response.data;
}

export async function updateDocumentTitle(
  documentId: string,
  title: string,
): Promise<DocumentListItem> {
  const response = await api.put<DocumentListItem>(`/documents/${documentId}`, { title });
  return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/documents/${documentId}`);
}

export async function retryDocumentProcessing(documentId: string): Promise<DocumentListItem> {
  const response = await api.post<DocumentListItem>(`/documents/${documentId}/retry`);
  return response.data;
}

export async function getDocumentMarkdown(documentId: string): Promise<string> {
  const response = await api.get<string>(`/documents/${documentId}/markdown`);
  return response.data;
}

