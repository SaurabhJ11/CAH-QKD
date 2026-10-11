import type { RecommendRequest, RecommendResponse, ProtocolResult } from '../types';
import { protocols } from '../data/protocols';
import { platforms } from '../data/platforms';

// Base key rates for protocols (normalized 0-1)
const protocolBaseRates: Record<string, number> = {
  'ab-qkd': 0.75,
  'b92': 0.70,
  'bb84': 0.85,
  'bbm92': 0.80,
  'ds6-qkd': 0.86,
  'decoy-bb84': 0.92,
  'eepm-qkd': 0.79,
  'sarg04': 0.78,
  'six-state': 0.88,
};

// Platform fidelity multipliers
const platformMultipliers: Record<string, number> = {
  'ionq_aria': 1.0,
  'ionq_harmony': 0.92,
  'rigetti_aspen_m3': 0.95,
  'oqc_lucy': 0.90,
};

function calculateSecureKeyRate(
  protocolId: string,
  distanceKm: number,
  platform: string,
  noiseFactor: number
): number {
  const baseRate = protocolBaseRates[protocolId] || 0.75;
  const platformMult = platformMultipliers[platform] || 0.9;
  
  // Distance attenuation (exponential decay)
  const distanceFactor = Math.exp(-distanceKm / 150);
  
  // Noise impact (inverse relationship)
  const noiseMult = 1 / (noiseFactor * 0.8);
  
  // Calculate final rate with some randomness for realism
  const rate = baseRate * platformMult * distanceFactor * noiseMult;
  
  // Add small random variation (+/- 5%)
  const variation = 0.95 + Math.random() * 0.1;
  
  // Clamp between 0 and 1
  return Math.max(0, Math.min(1, rate * variation));
}

export async function getRecommendations(request: RecommendRequest): Promise<RecommendResponse> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 600 + Math.random() * 400));
  
  // Calculate rates for all protocols
  const results: ProtocolResult[] = protocols.map((protocol) => ({
    name: protocol.name,
    secure_key_rate: calculateSecureKeyRate(
      protocol.id,
      request.distance_km,
      request.platform,
      request.noise_factor
    ),
    rank: 0,
  }));
  
  // Sort by rate descending and assign ranks
  results.sort((a, b) => b.secure_key_rate - a.secure_key_rate);
  results.forEach((result, index) => {
    result.rank = index + 1;
  });
  
  // Return top N
  const topN = results.slice(0, request.top_n);
  
  return {
    protocols: topN,
    request,
    timestamp: new Date().toISOString(),
  };
}

export async function getAllProtocolRates(
  distanceKm: number,
  platform: string,
  noiseFactor: number
): Promise<ProtocolResult[]> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 300 + Math.random() * 200));
  
  const results: ProtocolResult[] = protocols.map((protocol) => ({
    name: protocol.name,
    secure_key_rate: calculateSecureKeyRate(protocol.id, distanceKm, platform, noiseFactor),
    rank: 0,
  }));
  
  results.sort((a, b) => b.secure_key_rate - a.secure_key_rate);
  results.forEach((result, index) => {
    result.rank = index + 1;
  });
  
  return results;
}

export function getPlatformInfo(platformId: string) {
  return platforms.find((p) => p.id === platformId);
}
