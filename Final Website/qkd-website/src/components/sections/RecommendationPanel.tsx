import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button, Card, Slider, Select, Badge } from '../ui';
import { platformOptions } from '../../data/platforms';
import { getRecommendations } from '../../services/api';
import type { FormState, FormErrors, RecommendResponse, LoadingState } from '../../types';
import ProtocolComparison from './ProtocolComparison';

const DEFAULT_VALUES: FormState = {
  distance_km: 50,
  platform: 'ionq_aria',
  noise_factor: 1.5,
};

export default function RecommendationPanel() {
  const [formState, setFormState] = useState<FormState>(DEFAULT_VALUES);
  const [errors, setErrors] = useState<FormErrors>({});
  const [results, setResults] = useState<RecommendResponse | null>(null);
  const [previousResults, setPreviousResults] = useState<RecommendResponse | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Tracks how many protocols are in the list so we can make the
  // results panel scrollable only when there are more than 3.
  const resultsRef = useRef<HTMLDivElement>(null);

  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    if (formState.distance_km < 5 || formState.distance_km > 200) {
      newErrors.distance_km = 'Distance must be between 5 and 200 km';
    }

    if (!formState.platform) {
      newErrors.platform = 'Please select a platform';
    }

    if (formState.noise_factor < 0.5 || formState.noise_factor > 3.0) {
      newErrors.noise_factor = 'Noise factor must be between 0.5 and 3.0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formState]);

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoadingState('loading');
    setErrorMessage(null);

    try {
      const response = await getRecommendations({
        ...formState,
        top_n: 3,
      });

      // Shift current → previous before storing the new result
      setPreviousResults(results);
      setResults(response);
      setLoadingState('success');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'An error occurred');
      setLoadingState('error');
    }
  };

  const handleReset = () => {
    setFormState(DEFAULT_VALUES);
    setResults(null);
    setPreviousResults(null);
    setErrors({});
    setErrorMessage(null);
    setLoadingState('idle');
  };

  const updateField = <K extends keyof FormState>(field: K, value: FormState[K]) => {
    setFormState((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const protocolCount = results?.protocols.length ?? 0;
  const isScrollable = protocolCount > 3;

  return (
    <section id="recommendation" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-primary mb-4">
            Protocol Recommendation
          </h2>
          <p className="text-secondary/70 max-w-2xl mx-auto">
            Configure your experimental parameters and get AI-powered recommendations
            for the optimal QKD protocols.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card variant="glass" className="p-8">
              <h3 className="text-xl font-display font-semibold text-primary mb-6">
                Input Parameters
              </h3>

              <div className="space-y-6">
                <Slider
                  label="Distance"
                  value={formState.distance_km}
                  min={5}
                  max={200}
                  step={1}
                  unit=" km"
                  onChange={(value) => updateField('distance_km', value)}
                  error={errors.distance_km}
                />

                <Select
                  label="Quantum Platform"
                  options={platformOptions}
                  value={formState.platform}
                  onChange={(value) => updateField('platform', value)}
                  error={errors.platform}
                />

                <Slider
                  label="Noise Factor"
                  value={formState.noise_factor}
                  min={0.5}
                  max={3.0}
                  step={0.1}
                  onChange={(value) => updateField('noise_factor', value)}
                  error={errors.noise_factor}
                />

                <div className="flex gap-3 pt-4">
                  <Button
                    variant="primary"
                    onClick={handleSubmit}
                    isLoading={loadingState === 'loading'}
                    className="flex-1"
                  >
                    Recommend Top 3
                  </Button>
                  <Button variant="ghost" onClick={handleReset}>
                    Reset
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Results Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Card variant="glass" className="p-8 flex flex-col min-h-[400px]">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-display font-semibold text-primary">
                  Results
                </h3>
                {isScrollable && (
                  <span className="text-xs text-secondary/50">
                    {protocolCount} protocols — scroll to view all
                  </span>
                )}
              </div>

              {/* Scrollable results container: fixed height only when > 3 protocols */}
              <div
                ref={resultsRef}
                className={
                  isScrollable
                    ? 'overflow-y-auto max-h-[480px] pr-1 scrollbar-thin scrollbar-thumb-secondary/20 scrollbar-track-transparent'
                    : 'flex-1'
                }
              >
                <AnimatePresence mode="wait">
                  {loadingState === 'idle' && !results && (
                    <motion.div
                      key="empty"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center h-64 text-center"
                    >
                      <div className="w-16 h-16 mb-4 rounded-full bg-secondary-container/30 flex items-center justify-center">
                        <svg
                          className="w-8 h-8 text-secondary/50"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1.5}
                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                          />
                        </svg>
                      </div>
                      <p className="text-secondary/60">
                        Configure parameters and click "Recommend Top 3" to get results
                      </p>
                    </motion.div>
                  )}

                  {loadingState === 'loading' && (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center h-64"
                    >
                      <div className="w-12 h-12 border-3 border-primary/30 border-t-primary rounded-full animate-spin mb-4" />
                      <p className="text-secondary/60">Analyzing protocols...</p>
                    </motion.div>
                  )}

                  {loadingState === 'error' && (
                    <motion.div
                      key="error"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center h-64 text-center"
                    >
                      <div className="w-16 h-16 mb-4 rounded-full bg-error/20 flex items-center justify-center">
                        <svg
                          className="w-8 h-8 text-error"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      </div>
                      <p className="text-error mb-2">Error</p>
                      <p className="text-secondary/60 text-sm">{errorMessage}</p>
                    </motion.div>
                  )}

                  {loadingState === 'success' && results && (
                    <motion.div
                      key="results"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="space-y-4"
                    >
                      {results.protocols.map((protocol, index) => (
                        <motion.div
                          key={protocol.name}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.15 }}
                          className={`p-4 rounded-xl border ${
                            index === 0
                              ? 'bg-primary-container/20 border-primary/50'
                              : 'bg-surface-bright/50 border-secondary-container/30'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <div
                                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                                  index === 0
                                    ? 'bg-primary text-primary-on'
                                    : 'bg-secondary-container text-secondary-on-container'
                                }`}
                              >
                                {protocol.rank}
                              </div>
                              <div>
                                <h4 className="font-semibold text-primary">
                                  {protocol.name}
                                </h4>
                                {index === 0 && (
                                  <Badge variant="success" size="sm">
                                    Best Match
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4 mb-3">
                            <div className="bg-surface/50 rounded-lg p-3">
                              <div className="text-xs text-secondary/60 mb-1">
                                Secure Key Rate
                              </div>
                              <div className="font-mono text-sm font-semibold text-primary">
                                {protocol.secure_key_rate.toFixed(8)}
                              </div>
                            </div>
                            <div className="bg-surface/50 rounded-lg p-3">
                              <div className="text-xs text-secondary/60 mb-1">
                                Transmission
                              </div>
                              <div className="font-mono text-sm font-semibold text-primary">
                                {(protocol.transmission ?? 0).toFixed(8)}
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </Card>
          </motion.div>
        </div>

        {/* Comparison section — sits below the two-column grid */}
        <ProtocolComparison current={results} previous={previousResults} />
      </div>
    </section>
  );
}