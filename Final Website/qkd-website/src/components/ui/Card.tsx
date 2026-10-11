import type { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'glass' | 'elevated' | 'winner';
  animate?: boolean;
}

const cardVariants = {
  default: 'bg-surface-bright border border-secondary-container/30',
  glass: 'bg-surface-bright/30 backdrop-blur-md border border-secondary-container/30',
  elevated: 'bg-surface-bright border border-secondary-container/30 shadow-xl shadow-black/20',
  winner: 'bg-gradient-to-br from-primary-container/40 to-tertiary-container/30 border-2 border-primary/50',
};

export function Card({ children, className = '', variant = 'default', animate = true }: CardProps) {
  const baseClasses = `rounded-2xl p-6 ${cardVariants[variant]} ${className}`;

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className={baseClasses}
      >
        {children}
      </motion.div>
    );
  }

  return <div className={baseClasses}>{children}</div>;
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return <div className={`mb-4 ${className}`}>{children}</div>;
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export function CardTitle({ children, className = '' }: CardTitleProps) {
  return <h3 className={`text-xl font-display font-semibold text-primary ${className}`}>{children}</h3>;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return <div className={`text-secondary ${className}`}>{children}</div>;
}
