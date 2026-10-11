import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, Badge, ProgressBar } from '../ui';
import { protocols } from '../../data/protocols';
import { platformOptions } from '../../data/platforms';
import { fetchAllProtocolRates } from '../../services/api';
import type { ProtocolResult } from '../../types';

export default function ProtocolExplorer() {
  const [searchQuery, setSearchQuery] = useState('');
  const [protocolRates, setProtocolRates] = useState<ProtocolResult[]>([]);
  const [sortBy, setSortBy] = useState<'name' | 'rate'>('rate');
  const [selectedPlatform, setSelectedPlatform] = useState('ionq_aria');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchRates = async () => {
      setIsLoading(true);
      try {
        const rates = await fetchAllProtocolRates(100, selectedPlatform, 1.5);
        setProtocolRates(rates);
      } catch (error) {
        console.error('Failed to fetch rates:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRates();
  }, [selectedPlatform]);

  const filteredProtocols = useMemo(() => {
    let result = protocols.filter((p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.fullName.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Merge with rates
    const protocolsWithRates = result.map((p) => ({
      ...p,
      rate: protocolRates.find((r) => r.name === p.name)?.secure_key_rate ?? 0,
      rank: protocolRates.find((r) => r.name === p.name)?.rank ?? 10,
    }));

    // Sort
    if (sortBy === 'rate') {
      protocolsWithRates.sort((a, b) => b.rate - a.rate);
    } else {
      protocolsWithRates.sort((a, b) => a.name.localeCompare(b.name));
    }

    return protocolsWithRates;
  }, [searchQuery, protocolRates, sortBy]);

  const categoryColors = {
    'prepare-measure': 'primary',
    'entanglement-based': 'tertiary',
    'decoy-state': 'secondary',
  } as const;

  return (
    <section id="protocols" className="py-24 bg-surface-dim/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-primary mb-4">
            Protocol Explorer
          </h2>
          <p className="text-secondary/70 max-w-2xl mx-auto">
            Browse all 10 QKD protocols with their predicted secure key rates.
            Filter by name or sort by performance.
          </p>
        </motion.div>

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-col sm:flex-row gap-4 mb-8"
        >
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search protocols..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 pl-10 bg-surface-bright border border-secondary-container/50 rounded-lg text-secondary placeholder:text-secondary/50 focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary/50"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>

          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="px-4 py-3 bg-surface-bright border border-secondary-container/50 rounded-lg text-secondary focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            {platformOptions.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'name' | 'rate')}
            className="px-4 py-3 bg-surface-bright border border-secondary-container/50 rounded-lg text-secondary focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="rate">Sort by Rate</option>
            <option value="name">Sort by Name</option>
          </select>
        </motion.div>

        {/* Protocol Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProtocols.map((protocol, index) => (
            <motion.div
              key={protocol.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
            >
              <Card
                variant={protocol.rank === 1 ? 'winner' : 'default'}
                className="h-full hover:border-primary/40 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-display font-semibold text-primary">
                      {protocol.name}
                    </h3>
                    <p className="text-sm text-secondary/60">{protocol.fullName}</p>
                  </div>
                  <Badge variant={categoryColors[protocol.category]}>
                    {protocol.category.replace('-', ' ')}
                  </Badge>
                </div>

                <p className="text-sm text-secondary/70 mb-4">{protocol.description}</p>

                <div className="mt-auto">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-secondary/60">Predicted Rate</span>
                    <span className="text-sm font-semibold text-primary">
                      {isLoading ? '...' : `${(protocol.rate * 100).toFixed(1)}%`}
                    </span>
                  </div>
                  <ProgressBar
                    value={protocol.rate}
                    variant={protocol.rank <= 3 ? 'gradient' : 'primary'}
                    size="sm"
                    animate={!isLoading}
                  />
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        {filteredProtocols.length === 0 && (
          <div className="text-center py-12">
            <p className="text-secondary/60">No protocols match your search.</p>
          </div>
        )}
      </div>
    </section>
  );
}
