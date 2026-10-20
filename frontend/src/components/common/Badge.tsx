import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'brand' | 'emerald' | 'amber' | 'rose' | 'slate' | 'cyan';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = 'brand',
  size = 'md',
  ...props
}) => {
  const variants = {
    brand: 'bg-brand-500/15 text-brand-300 border-brand-500/30',
    emerald: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    amber: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    rose: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
    slate: 'bg-slate-800/80 text-slate-300 border-slate-700/60',
    cyan: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  };

  const sizes = {
    sm: 'text-[11px] font-medium px-2 py-0.5 rounded-md border',
    md: 'text-xs font-semibold px-2.5 py-1 rounded-lg border',
  };

  return (
    <span
      className={twMerge(clsx('inline-flex items-center gap-1.5 font-medium tracking-wide', variants[variant], sizes[size], className))}
      {...props}
    >
      {children}
    </span>
  );
};
