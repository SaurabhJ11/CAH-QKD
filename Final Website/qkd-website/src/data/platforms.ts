import type { Platform } from '../types';

export const platforms: Platform[] = [
  {
    id: 'ionq_aria',
    label: 'IonQ Aria',
    fidelity: '99.5%',
    t1: '10-100s',
    t2: '1-10s',
    description: 'High-fidelity trapped ion quantum computer with excellent coherence times.',
  },
  {
    id: 'ionq_harmony',
    label: 'IonQ Harmony',
    fidelity: '98%',
    t1: '~10s',
    t2: '~1s',
    description: 'Reliable trapped ion system optimized for quantum networking.',
  },
  {
    id: 'rigetti_aspen_m3',
    label: 'Rigetti Aspen-M3',
    fidelity: '99%',
    t1: '20-80μs',
    t2: '10-40μs',
    description: 'Superconducting qubit processor with fast gate operations.',
  },
  {
    id: 'oqc_lucy',
    label: 'OQC Lucy',
    fidelity: '98.5%',
    t1: '50-150μs',
    t2: '20-80μs',
    description: 'Coaxmon-based superconducting system with scalable architecture.',
  },
];

export const platformOptions = platforms.map((p) => ({
  value: p.id,
  label: p.label,
}));
