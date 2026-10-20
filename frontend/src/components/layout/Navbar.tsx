import React from 'react';
import { Link } from 'react-router-dom';
import { Bot, Sparkles, Plus, Cpu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../common/Button';

export const Navbar: React.FC = () => {
  const { user } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-30 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {/* System status pill */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-medium text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-brand-400" />
            Adaptive AI Engine: <strong className="text-emerald-400 font-semibold">Active</strong>
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Link to="/setup">
          <Button size="sm" variant="primary" leftIcon={<Plus className="w-3.5 h-3.5" />}>
            New Interview
          </Button>
        </Link>

        {user && (
          <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
            <div className="w-7 h-7 rounded-full bg-brand-600/30 border border-brand-500/40 flex items-center justify-center text-xs font-bold text-brand-300">
              {user.name.charAt(0)}
            </div>
            <span className="text-xs font-semibold text-slate-200 hidden sm:inline">
              {user.name}
            </span>
          </div>
        )}
      </div>
    </header>
  );
};
