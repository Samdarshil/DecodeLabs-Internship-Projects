/**
 * src/services/api.ts — Type-safe API client.
 *
 * All requests proxied through Vite devServer (/api → localhost:8000).
 * In production, set VITE_API_URL to the deployed backend URL.
 */
import axios, { AxiosError } from 'axios'

export const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Types ─────────────────────────────────────────────────────────────────────

export interface FeatureImportance {
  feature:          string
  value:            number
  shap_value:       number
  impact_direction: 'positive' | 'negative'
}

export interface PredictionResult {
  prediction:            'Malignant' | 'Benign'
  prediction_class:      0 | 1
  confidence:            number
  probability_malignant: number
  probability_benign:    number
  top_features:          FeatureImportance[]
  model_version:         string
  inference_time_ms:     number
}

export interface ModelMetrics {
  version:            string
  model_type:         string
  accuracy:           number
  f1_weighted:        number
  roc_auc:            number
  cv_accuracy_mean:   number
  cv_accuracy_std:    number
  train_samples:      number
  test_samples:       number
  feature_names:      string[]
  target_names:       string[]
}

export interface HealthStatus {
  status:        string
  model_loaded:  boolean
  model_version: string | null
}

// ── Input features (all 30 Wisconsin fields) ─────────────────────────────────

export interface PredictionInput {
  radius_mean:             number
  texture_mean:            number
  perimeter_mean:          number
  area_mean:               number
  smoothness_mean:         number
  compactness_mean:        number
  concavity_mean:          number
  concave_points_mean:     number
  symmetry_mean:           number
  fractal_dimension_mean:  number
  radius_se:               number
  texture_se:              number
  perimeter_se:            number
  area_se:                 number
  smoothness_se:           number
  compactness_se:          number
  concavity_se:            number
  concave_points_se:       number
  symmetry_se:             number
  fractal_dimension_se:    number
  radius_worst:            number
  texture_worst:           number
  perimeter_worst:         number
  area_worst:              number
  smoothness_worst:        number
  compactness_worst:       number
  concavity_worst:         number
  concave_points_worst:    number
  symmetry_worst:          number
  fractal_dimension_worst: number
}

// ── API calls ────────────────────────────────────────────────────────────────

export async function runPrediction(input: PredictionInput): Promise<PredictionResult> {
  const { data } = await client.post<PredictionResult>('/predict', input)
  return data
}

export async function fetchMetrics(): Promise<ModelMetrics> {
  const { data } = await client.get<ModelMetrics>('/metrics')
  return data
}

export async function fetchHealth(): Promise<HealthStatus> {
  const { data } = await client.get<HealthStatus>('/health')
  return data
}

export async function triggerRetrain(): Promise<{ status: string; metrics: ModelMetrics }> {
  const { data } = await client.post('/train')
  return data
}

// ── Error helper ─────────────────────────────────────────────────────────────

export function getErrorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail?.errors)) return detail.errors.join(', ')
    if (err.response?.status === 503) return 'Model not loaded. Run python train.py on the backend.'
    if (err.response?.status === 429) return 'Rate limit exceeded. Please wait a moment.'
    return err.message
  }
  return String(err)
}
