import type { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'primary' | 'secondary' | 'tertiary' | 'success' | 'warning';
  size?: 'sm' | 'md';
  className?: string;
}

const variants = {
  default: 'bg-surface-bright text-secondary border border-secondary-container/50',
  primary: 'bg-primary-container text-primary-on-container',
  secondary: 'bg-secondary-container text-secondary-on-container',
  tertiary: 'bg-tertiary-container text-tertiary-on-container',
  success: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
  warning: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
};

const sizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
};

export function Badge({ children, variant = 'default', size = 'md', className = '' }: BadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center justify-center
        font-medium rounded-full
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
    >
      {children}
    </span>
  );
}
