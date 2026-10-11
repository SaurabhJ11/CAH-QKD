// Protocol Types
export interface Protocol {
  id: string;
  name: string;
  fullName: string;
  description: string;
  category: 'prepare-measure' | 'entanglement-based' | 'decoy-state';
}

// Platform Types
export interface Platform {
  id: string;
  label: string;
  fidelity: string;
  t1: string;
  t2: string;
  description: string;
}

// Recommendation Types
export interface RecommendRequest {
  distance_km: number;
  platform: string;
  noise_factor: number;
  top_n: number;
}

export interface ProtocolResult {
  name: string;
  secure_key_rate: number;
  transmission?: number;
  rank: number;
}

export interface RecommendResponse {
  protocols: ProtocolResult[];
  request: RecommendRequest;
  timestamp: string;
}

// Model Metrics Types
export interface ModelMetric {
  label: string;
  value: string | number;
  description: string;
  icon?: string;
}

// Form State Types
export interface FormState {
  distance_km: number;
  platform: string;
  noise_factor: number;
}

export interface FormErrors {
  distance_km?: string;
  platform?: string;
  noise_factor?: string;
}

// API State Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface ApiState<T> {
  data: T | null;
  loading: LoadingState;
  error: string | null;
}
