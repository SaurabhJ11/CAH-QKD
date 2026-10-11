import type { ModelMetric } from '../types';

export const modelMetrics: ModelMetric[] = [
  {
    label: 'Algorithm',
    value: 'XGBoost',
    description: 'Gradient boosting ensemble method for accurate predictions',
    icon: '🧠',
  },
  {
    label: 'Dataset Size',
    value: '40,000',
    description: 'Training samples across various QKD configurations',
    icon: '📊',
  },
  {
    label: 'R² Score',
    value: 0.967,
    description: 'Coefficient of determination indicating model fit',
    icon: '📈',
  },
  {
    label: 'MAE',
    value: 0.0023,
    description: 'Mean Absolute Error in secure key rate prediction',
    icon: '📉',
  },
  {
    label: 'RMSE',
    value: 0.0041,
    description: 'Root Mean Square Error for prediction accuracy',
    icon: '📐',
  },
  {
    label: 'Features',
    value: 21,
    description: 'Input features including distance, noise, and platform specs',
    icon: '🔢',
  },
];
