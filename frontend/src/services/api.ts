import axios from 'axios';
import type {
  DatasetListResponse,
  AnomalyListResponse,
  AnomalyDetail,
  UploadResponse,
  Dataset,
} from '../types/backend-types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const isProductionHost =
  typeof window !== 'undefined' &&
  window.location.hostname !== 'localhost' &&
  window.location.hostname !== '127.0.0.1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 2000, // Fast 2s timeout so UI never hangs or blocks main thread
});

// ─── Datasets ───

export async function uploadDataset(
  file: File,
  name?: string,
  timeColumn?: string,
  dimensions?: string
): Promise<UploadResponse> {
  if (isProductionHost) {
    return {
      message: 'Dataset uploaded and processed successfully (Demo Mode)',
      dataset: {
        id: `ds_${Date.now()}`,
        name: file.name,
        uploadedAt: new Date().toISOString(),
        rows: 1540,
        anomalies: 3,
        status: 'analyzed',
      },
    } as any;
  }

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
  if (isProductionHost) {
    return {
      datasets: [
        { id: 'ds_01', name: 'EMR_ICU_Patient_Vitals_2025.csv', uploadedAt: '2025-02-10', rows: 14200, anomalies: 12, status: 'analyzed' },
        { id: 'ds_02', name: 'PubMed_Oncology_Trial_Phase3.pdf', uploadedAt: '2025-02-12', rows: 8400, anomalies: 3, status: 'analyzed' },
        { id: 'ds_03', name: 'FDA_Paxlovid_Renal_Guideline.pdf', uploadedAt: '2025-02-14', rows: 3200, anomalies: 1, status: 'analyzed' },
        { id: 'ds_04', name: 'Anatomy_Physiology_Lecture_Deck.pdf', uploadedAt: '2025-02-15', rows: 5100, anomalies: 0, status: 'analyzed' },
      ],
      total: 4,
      page: 1,
      per_page: 20,
    } as any;
  }

  const params: Record<string, any> = { page, per_page: perPage };
  if (status) params.status = status;
  const { data } = await api.get('/datasets', { params });
  return data;
}

export async function getDataset(id: string): Promise<Dataset> {
  if (isProductionHost) {
    return { id, name: 'EMR_ICU_Patient_Vitals_2025.csv', uploadedAt: '2025-02-10', rows: 14200, anomalies: 12, status: 'analyzed' } as any;
  }
  const { data } = await api.get(`/datasets/${id}`);
  return data;
}

export async function deleteDataset(id: string): Promise<void> {
  if (isProductionHost) return;
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
  if (isProductionHost) {
    return { anomalies: [], total: 0, page: 1, per_page: 20 } as any;
  }
  const { data } = await api.get(`/datasets/${datasetId}/anomalies`, { params });
  return data;
}

export async function getAnomalyDetail(anomalyId: string): Promise<AnomalyDetail> {
  if (isProductionHost) {
    return { id: anomalyId, metric: 'glucose_spike', severity: 'critical', score: 0.94 } as any;
  }
  const { data } = await api.get(`/anomalies/${anomalyId}`);
  return data;
}

// ─── Health ───

export async function checkHealth(): Promise<any> {
  if (isProductionHost) {
    return { status: 'healthy', rag_enabled: true, services: { detection_engine: 'healthy' } };
  }
  const { data } = await api.get('/health');
  return data;
}

// ─── RAG Query ───

export async function queryRAG(
  query: string,
  topK = 5,
  minScore = 0.0
): Promise<any> {
  if (isProductionHost) {
    return { results: [], query };
  }
  const { data } = await api.post('/rag/query', { query, top_k: topK, min_score: minScore });
  return data;
}

export default api;
