import type { Protocol } from '../types';

export const protocols: Protocol[] = [
  {
    id: 'ab-qkd',
    name: 'AB-QKD',
    fullName: 'Asymmetric Biased QKD',
    description: 'Optimized protocol with asymmetric basis selection for improved key rates.',
    category: 'prepare-measure',
  },
  {
    id: 'b92',
    name: 'B92',
    fullName: 'Bennett 1992 Protocol',
    description: 'Simplified two-state protocol using non-orthogonal quantum states.',
    category: 'prepare-measure',
  },
  {
    id: 'bb84',
    name: 'BB84',
    fullName: 'Bennett-Brassard 1984',
    description: 'The original QKD protocol using four quantum states in two bases.',
    category: 'prepare-measure',
  },
  {
    id: 'bbm92',
    name: 'BBM92',
    fullName: 'Bennett-Brassard-Mermin 1992',
    description: 'Entanglement-based version of BB84 using EPR pairs.',
    category: 'entanglement-based',
  },
  {
    id: 'ds6-qkd',
    name: 'DS6-QKD',
    fullName: 'Distributed Six-State QKD',
    description: 'Enhanced security protocol using six quantum states.',
    category: 'prepare-measure',
  },
  {
    id: 'decoy-bb84',
    name: 'Decoy-BB84',
    fullName: 'Decoy State BB84',
    description: 'BB84 enhanced with decoy states to detect photon number attacks.',
    category: 'decoy-state',
  },
  {
    id: 'eepm-qkd',
    name: 'EEPM-QKD',
    fullName: 'Efficient Entanglement Protocol',
    description: 'Optimized entanglement-based protocol for practical implementations.',
    category: 'entanglement-based',
  },
  {
    id: 'sarg04',
    name: 'SARG04',
    fullName: 'Scarani-Acín-Ribordy-Gisin 2004',
    description: 'Four-state protocol with enhanced resistance to PNS attacks.',
    category: 'prepare-measure',
  },
  {
    id: 'six-state',
    name: 'Six-State',
    fullName: 'Six-State Protocol',
    description: 'Extension of BB84 using three mutually unbiased bases.',
    category: 'prepare-measure',
  },
];
