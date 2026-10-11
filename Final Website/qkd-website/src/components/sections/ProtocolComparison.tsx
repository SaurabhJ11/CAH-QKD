import { motion, AnimatePresence } from 'framer-motion';
import { Card, Badge } from '../ui';
import type { RecommendResponse } from '../../types';

interface Protocol {
  name: string;
  rank: number;
  secure_key_rate: number;
  transmission?: number;
}

interface ProtocolComparisonSectionProps {
  current: RecommendResponse | null;
  previous: RecommendResponse | null;
}

function getRankChange(protocolName: string, current: Protocol[], previous: Protocol[]): number | null {
  const prevEntry = previous.find((p) => p.name === protocolName);
  const currEntry = current.find((p) => p.name === protocolName);
  if (!prevEntry || !currEntry) return null;
  return prevEntry.rank - currEntry.rank; // positive = moved up
}

function getKeyRateDelta(name: string, current: Protocol[], previous: Protocol[]): number | null {
  const prev = previous.find((p) => p.name === name);
  const curr = current.find((p) => p.name === name);
  if (!prev || !curr) return null;
  return curr.secure_key_rate - prev.secure_key_rate;
}

function DeltaBadge({ delta }: { delta: number | null }) {
  if (delta === null) return <span className="text-xs text-secondary/40 italic">new</span>;
  if (delta === 0) return <span className="text-xs text-secondary/50">—</span>;

  const isPositive = delta > 0;
  return (
    <span
      className={`inline-flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded-md ${
        isPositive
          ? 'bg-emerald-500/15 text-emerald-400'
          : 'bg-rose-500/15 text-rose-400'
      }`}
    >
      {isPositive ? '▲' : '▼'} {Math.abs(delta).toFixed(8)}
    </span>
  );
}

function RankShiftIndicator({ shift }: { shift: number | null }) {
  if (shift === null)
    return (
      <span className="text-[10px] font-medium uppercase tracking-wider text-secondary/40 italic">
        New
      </span>
    );
  if (shift === 0)
    return (
      <span className="text-[10px] font-medium uppercase tracking-wider text-secondary/40">
        Same
      </span>
    );

  const isUp = shift > 0;
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider ${
        isUp ? 'text-emerald-400' : 'text-rose-400'
      }`}
    >
      {isUp ? '↑' : '↓'} {Math.abs(shift)} rank{Math.abs(shift) > 1 ? 's' : ''}
    </span>
  );
}

export default function ProtocolComparison({
  current,
  previous,
}: ProtocolComparisonSectionProps) {
  const hasHistory = current !== null && previous !== null;
  const hasCurrent = current !== null;

  // Collect all unique protocol names across both runs
  const allNames = Array.from(
    new Set([
      ...(current?.protocols.map((p) => p.name) ?? []),
      ...(previous?.protocols.map((p) => p.name) ?? []),
    ])
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="mt-10"
    >
      <div className="mb-5 flex items-center gap-3">
        <h3 className="text-lg font-display font-semibold text-primary">
          Run Comparison
        </h3>
        {hasHistory && (
          <Badge variant="secondary" size="sm">
            Previous vs Current
          </Badge>
        )}
      </div>

      <AnimatePresence mode="wait">
        {/* Empty state — no runs yet */}
        {!hasCurrent && (
          <motion.div
            key="no-history"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card variant="glass" className="p-8">
              <div className="flex flex-col items-center justify-center gap-3 py-6 text-center">
                <div className="w-12 h-12 rounded-full bg-secondary-container/25 flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-secondary/40"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                </div>
                <p className="text-secondary/50 text-sm max-w-xs">
                  No history present. Run the recommender at least twice to compare results across parameter changes.
                </p>
              </div>
            </Card>
          </motion.div>
        )}

        {/* One run done — waiting for a second */}
        {hasCurrent && !hasHistory && (
          <motion.div
            key="one-run"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card variant="glass" className="p-8">
              <div className="flex flex-col items-center justify-center gap-3 py-6 text-center">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-primary/50"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                </div>
                <p className="text-secondary/50 text-sm max-w-xs">
                  First run saved. Adjust your parameters and run again to see a side-by-side comparison.
                </p>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Full comparison */}
        {hasHistory && (
          <motion.div
            key="comparison"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card variant="glass" className="p-6 overflow-x-auto">
              {/* Column headers */}
              <div className="grid grid-cols-[1fr_auto_1fr] gap-4 mb-4 text-[11px] font-semibold uppercase tracking-widest text-secondary/40">
                <div className="text-center">Previous Run</div>
                <div className="text-center w-24">Protocol</div>
                <div className="text-center">Current Run</div>
              </div>

              <div className="space-y-3">
                {allNames.map((name, i) => {
                  const prevProtocol = previous!.protocols.find((p) => p.name === name);
                  const currProtocol = current!.protocols.find((p) => p.name === name);
                  const rankShift = getRankChange(name, current!.protocols, previous!.protocols);
                  const keyDelta = getKeyRateDelta(name, current!.protocols, previous!.protocols);
                  const isTopCurrent = currProtocol?.rank === 1;
                  const isTopPrevious = prevProtocol?.rank === 1;

                  return (
                    <motion.div
                      key={name}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.08 }}
                      className={`grid grid-cols-[1fr_auto_1fr] gap-4 items-center rounded-xl px-4 py-3 border ${
                        isTopCurrent
                          ? 'bg-primary-container/15 border-primary/30'
                          : 'bg-surface-bright/30 border-secondary-container/20'
                      }`}
                    >
                      {/* Previous side */}
                      <div className="text-right space-y-1">
                        {prevProtocol ? (
                          <>
                            <div className="flex items-center justify-end gap-2">
                              {isTopPrevious && (
                                <Badge variant="success" size="sm">Best</Badge>
                              )}
                              <span className="text-xs font-mono text-secondary/60">
                                #{prevProtocol.rank}
                              </span>
                            </div>
                            <div className="text-xs font-mono text-secondary/70">
                              SKR: {prevProtocol.secure_key_rate.toFixed(8)}
                            </div>
                            <div className="text-xs font-mono text-secondary/50">
                              Tx: {(prevProtocol.transmission ?? 0).toFixed(8)}
                            </div>
                          </>
                        ) : (
                          <span className="text-xs text-secondary/30 italic">not ranked</span>
                        )}
                      </div>

                      {/* Center: protocol name + shift */}
                      <div className="flex flex-col items-center gap-1 w-24">
                        <span className="text-xs font-semibold text-primary text-center leading-tight">
                          {name}
                        </span>
                        <RankShiftIndicator shift={rankShift} />
                        {keyDelta !== null && (
                          <DeltaBadge delta={keyDelta} />
                        )}
                      </div>

                      {/* Current side */}
                      <div className="space-y-1">
                        {currProtocol ? (
                          <>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono text-secondary/60">
                                #{currProtocol.rank}
                              </span>
                              {isTopCurrent && (
                                <Badge variant="success" size="sm">Best</Badge>
                              )}
                            </div>
                            <div className="text-xs font-mono text-secondary/70">
                              SKR: {currProtocol.secure_key_rate.toFixed(8)}
                            </div>
                            <div className="text-xs font-mono text-secondary/50">
                              Tx: {(currProtocol.transmission ?? 0).toFixed(8)}
                            </div>
                          </>
                        ) : (
                          <span className="text-xs text-secondary/30 italic">not ranked</span>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Footer legend */}
              <div className="mt-5 pt-4 border-t border-secondary-container/20 flex flex-wrap gap-4 text-[11px] text-secondary/40">
                <span className="flex items-center gap-1.5">
                  <span className="text-emerald-400 font-semibold">▲</span> SKR improved
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="text-rose-400 font-semibold">▼</span> SKR declined
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="text-emerald-400 font-semibold">↑</span> Rank rose
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="text-rose-400 font-semibold">↓</span> Rank fell
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="italic">new</span> — appeared only in one run
                </span>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}