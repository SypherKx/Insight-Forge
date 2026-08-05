import axios from 'axios';
import type {
  DatasetListResponse,
  AnomalyListResponse,
  AnomalyDetail,
  UploadResponse,
  Dataset,
} from '../types/backend-types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 3000, // 3s timeout so UI never hangs when backend is offline
});

// ─── Datasets ───

export async function uploadDataset(
  file: File,
  name?: string,
  timeColumn?: string,
  dimensions?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (name) formData.append('name', name);
  if (timeColumn) formData.append('time_column', timeColumn);
  if (dimensions) formData.append('dimensions', dimensions);

  const { data } = await api.post('/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getDatasets(
  page = 1,
  perPage = 20,
  status?: string
): Promise<DatasetListResponse> {
  const params: Record<string, any> = { page, per_page: perPage };
  if (status) params.status = status;
  const { data } = await api.get('/datasets', { params });
  return data;
}

export async function getDataset(id: string): Promise<Dataset> {
  const { data } = await api.get(`/datasets/${id}`);
  return data;
}

export async function deleteDataset(id: string): Promise<void> {
  await api.delete(`/datasets/${id}`);
}

// ─── Anomalies ───

export async function getAnomalies(
  datasetId: string,
  params?: {
    severity_min?: number;
    anomaly_type?: string;
    metric?: string;
    page?: number;
    per_page?: number;
  }
): Promise<AnomalyListResponse> {
  const { data } = await api.get(`/datasets/${datasetId}/anomalies`, { params });
  return data;
}

export async function getAnomalyDetail(anomalyId: string): Promise<AnomalyDetail> {
  const { data } = await api.get(`/anomalies/${anomalyId}`);
  return data;
}

// ─── Health ───

export async function checkHealth(): Promise<any> {
  const { data } = await api.get('/health');
  return data;
}

// ─── RAG Query ───

export async function queryRAG(
  query: string,
  topK = 5,
  minScore = 0.0
): Promise<any> {
  const { data } = await api.post('/rag/query', { query, top_k: topK, min_score: minScore });
  return data;
}

export default api;
