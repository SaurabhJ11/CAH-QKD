import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, Tooltip } from '../ui';
import { platforms } from '../../data/platforms';

export default function HardwareComparison() {
  const [hoveredPlatform, setHoveredPlatform] = useState<string | null>(null);

  return (
    <section id="hardware" className="py-24 bg-surface-dim/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-primary mb-4">
            Hardware Comparison
          </h2>
          <p className="text-secondary/70 max-w-2xl mx-auto">
            Compare the quantum computing platforms supported by our prediction model.
          </p>
        </motion.div>

        {/* Desktop Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="hidden md:block"
        >
          <Card variant="glass" className="p-8">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-secondary-container/30">
                    <th className="text-left py-4 px-4 text-sm font-semibold text-primary">
                      Platform
                    </th>
                    <th className="text-center py-4 px-4 text-sm font-semibold text-primary">
                      <Tooltip content="Gate fidelity - accuracy of quantum operations">
                        <span className="cursor-help border-b border-dotted border-primary/50">
                          Fidelity
                        </span>
                      </Tooltip>
                    </th>
                    <th className="text-center py-4 px-4 text-sm font-semibold text-primary">
                      <Tooltip content="Relaxation time - how long qubits maintain energy state">
                        <span className="cursor-help border-b border-dotted border-primary/50">
                          T1 Time
                        </span>
                      </Tooltip>
                    </th>
                    <th className="text-center py-4 px-4 text-sm font-semibold text-primary">
                      <Tooltip content="Dephasing time - how long qubits maintain phase coherence">
                        <span className="cursor-help border-b border-dotted border-primary/50">
                          T2 Time
                        </span>
                      </Tooltip>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {platforms.map((platform, index) => (
                    <motion.tr
                      key={platform.id}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.1 }}
                      className={`border-b border-secondary-container/20 transition-colors ${
                        hoveredPlatform === platform.id ? 'bg-primary-container/10' : ''
                      }`}
                      onMouseEnter={() => setHoveredPlatform(platform.id)}
                      onMouseLeave={() => setHoveredPlatform(null)}
                    >
                      <td className="py-4 px-4">
                        <div>
                          <span className="font-semibold text-primary">
                            {platform.label}
                          </span>
                          <p className="text-xs text-secondary/60 mt-1">
                            {platform.description}
                          </p>
                        </div>
                      </td>
                      <td className="text-center py-4 px-4">
                        <span className="inline-flex items-center justify-center px-3 py-1 bg-primary-container/30 rounded-full text-sm font-medium text-primary">
                          {platform.fidelity}
                        </span>
                      </td>
                      <td className="text-center py-4 px-4 text-secondary">
                        {platform.t1}
                      </td>
                      <td className="text-center py-4 px-4 text-secondary">
                        {platform.t2}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </motion.div>

        {/* Mobile Cards */}
        <div className="md:hidden grid gap-4">
          {platforms.map((platform, index) => (
            <motion.div
              key={platform.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <Card variant="glass">
                <h3 className="text-lg font-semibold text-primary mb-2">
                  {platform.label}
                </h3>
                <p className="text-sm text-secondary/60 mb-4">{platform.description}</p>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-xs text-secondary/60 mb-1">Fidelity</div>
                    <div className="text-sm font-semibold text-primary">
                      {platform.fidelity}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-secondary/60 mb-1">T1</div>
                    <div className="text-sm text-secondary">{platform.t1}</div>
                  </div>
                  <div>
                    <div className="text-xs text-secondary/60 mb-1">T2</div>
                    <div className="text-sm text-secondary">{platform.t2}</div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Legend */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="mt-8 p-4 bg-surface-bright/30 rounded-lg border border-secondary-container/20"
        >
          <h4 className="text-sm font-semibold text-primary mb-2">Understanding the Metrics</h4>
          <div className="grid sm:grid-cols-3 gap-4 text-sm text-secondary/70">
            <div>
              <strong className="text-secondary">Fidelity:</strong> Measures how accurately the quantum hardware performs operations.
            </div>
            <div>
              <strong className="text-secondary">T1 (Relaxation):</strong> Time before a qubit loses its excited state energy.
            </div>
            <div>
              <strong className="text-secondary">T2 (Coherence):</strong> Time before a qubit loses its quantum phase information.
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
