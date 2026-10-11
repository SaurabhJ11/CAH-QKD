import { motion } from 'framer-motion';
import { Card } from '../ui';
import { modelMetrics } from '../../data/modelMetrics';

export default function ModelOverview() {
  return (
    <section id="model" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-primary mb-4">
            Model Overview
          </h2>
          <p className="text-secondary/70 max-w-2xl mx-auto">
            Our prediction model is trained on extensive QKD simulation data
            to provide accurate secure key rate estimates.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {modelMetrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
            >
              <Card
                variant="glass"
                className="h-full text-center"
              >
                <div className="text-4xl mb-4">{metric.icon}</div>
                <h3 className="text-sm font-medium text-secondary/60 uppercase tracking-wider mb-2">
                  {metric.label}
                </h3>
                <div className="text-3xl font-display font-bold text-primary mb-2">
                  {typeof metric.value === 'number'
                    ? metric.value < 1
                      ? metric.value.toFixed(4)
                      : metric.value.toLocaleString()
                    : metric.value}
                </div>
                <p className="text-sm text-secondary/60">{metric.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Model Architecture Visual */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-12"
        >
          <Card variant="glass" className="p-8">
            <h3 className="text-xl font-display font-semibold text-primary mb-6 text-center">
              Prediction Pipeline
            </h3>
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              {[
                { icon: '📊', label: 'Input Features', desc: 'Distance, Platform, Noise' },
                { icon: '⚙️', label: 'Feature Engineering', desc: '21 derived features' },
                { icon: '🌲', label: 'XGBoost Model', desc: 'Gradient boosting ensemble' },
                { icon: '📈', label: 'Prediction', desc: 'Secure key rate output' },
              ].map((step, index) => (
                <div key={step.label} className="flex items-center gap-5">
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.5 + index * 0.1, type: 'spring' }}
                    className="w-30 h-30 rounded-2xl bg-primary-container/30 border border-primary/30 flex flex-col items-center justify-center"
                  >
                    <span className="text-2xl">{step.icon}</span>
                    <span className="text-xs text-primary mt-1">{step.label}</span>
                  </motion.div>
                  {index < 3 && (
                    <svg
                      className="w-8 h-8 text-primary/40 hidden md:block"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 7l5 5m0 0l-5 5m5-5H6"
                      />
                    </svg>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  );
}
