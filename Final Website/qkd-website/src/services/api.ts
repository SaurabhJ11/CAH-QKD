import type { RecommendRequest, RecommendResponse, ProtocolResult } from '../types';
import { getRecommendations as mockGetRecommendations, getAllProtocolRates as mockGetAllProtocolRates } from './mockService';

// Environment flag to switch between mock and real API
// Set to false to use the real FastAPI backend at http://localhost:8000
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API === 'true';
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

/**
 * Recommend top protocols based on input parameters
 */
export async function getRecommendations(
  request: RecommendRequest
): Promise<RecommendResponse> {
  if (USE_MOCK) {
    return mockGetRecommendations(request);
  }

  const response = await fetch(`${API_BASE_URL}/api/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get all protocol predictions
 */
export async function fetchAllProtocolRates(
  distance_km: number,
  platform: string,
  noise_factor: number
): Promise<ProtocolResult[]> {
  if (USE_MOCK) {
    return mockGetAllProtocolRates(distance_km, platform, noise_factor);
  }

  const response = await fetch(
    `${API_BASE_URL}/api/protocols?distance=${distance_km}&platform=${platform}&noise=${noise_factor}`
  );

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
