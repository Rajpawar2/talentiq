import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'interactive';
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = 'default',
  ...props
}) => {
  const variants = {
    default: 'bg-slate-900/80 border border-slate-800/80 rounded-2xl shadow-xl shadow-black/20',
    glass: 'glass-card rounded-2xl shadow-xl',
    interactive: 'bg-slate-900/80 border border-slate-800/80 hover:border-slate-700/90 rounded-2xl shadow-xl hover:shadow-2xl hover:shadow-brand-500/5 transition-all duration-300',
  };

  return (
    <div className={twMerge(clsx(variants[variant], 'p-5 sm:p-6', className))} {...props}>
      {children}
    </div>
  );
};
