import React from 'react';

export const Skeleton: React.FC<{ className?: string }> = ({ className = 'h-4 w-full' }) => {
  return (
    <div className={`animate-pulse bg-slate-800/80 rounded-xl ${className}`} />
  );
};

export const EmptyState: React.FC<{
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
}> = ({ icon, title, description, actionText, onAction }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30">
      {icon && <div className="p-3 bg-slate-800/80 text-brand-400 rounded-2xl mb-4">{icon}</div>}
      <h4 className="text-base font-bold text-white mb-1.5">{title}</h4>
      <p className="text-xs sm:text-sm text-slate-400 max-w-sm mb-5">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 text-xs font-semibold rounded-xl bg-brand-600 hover:bg-brand-500 text-white transition-all shadow-md shadow-brand-500/20"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};

export const ErrorState: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
}> = ({ title = 'Something went wrong', message, onRetry }) => {
  return (
    <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-500/30 text-rose-200 text-center">
      <h4 className="text-sm font-bold text-rose-400 mb-1">{title}</h4>
      <p className="text-xs text-rose-300/80 mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-1.5 text-xs font-semibold rounded-xl bg-rose-600/80 hover:bg-rose-500 text-white transition-all"
        >
          Retry
        </button>
      )}
    </div>
  );
};
