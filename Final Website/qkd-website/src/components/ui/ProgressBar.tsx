import { motion } from 'framer-motion';

interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showValue?: boolean;
  variant?: 'primary' | 'secondary' | 'tertiary' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  animate?: boolean;
}

const variants = {
  primary: 'bg-primary',
  secondary: 'bg-secondary',
  tertiary: 'bg-tertiary',
  gradient: 'bg-gradient-to-r from-primary via-tertiary to-primary',
};

const sizes = {
  sm: 'h-1.5',
  md: 'h-2.5',
  lg: 'h-4',
};

export function ProgressBar({
  value,
  max = 100,
  label,
  showValue = true,
  variant = 'primary',
  size = 'md',
  className = '',
  animate = true,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={`space-y-1 ${className}`}>
      {(label || showValue) && (
        <div className="flex justify-between items-center text-sm">
          {label && <span className="text-secondary-on-container font-medium">{label}</span>}
          {showValue && <span className="text-primary tabular-nums">{percentage.toFixed(1)}%</span>}
        </div>
      )}

      <div
        className={`w-full rounded-full bg-secondary-container/30 overflow-hidden ${sizes[size]}`}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={label}
      >
        {animate ? (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-full rounded-full ${variants[variant]}`}
          />
        ) : (
          <div className={`h-full rounded-full ${variants[variant]}`} style={{ width: `${percentage}%` }} />
        )}
      </div>
    </div>
  );
}
