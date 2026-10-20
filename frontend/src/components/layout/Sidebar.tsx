import React from 'react';
import { NavLink, useNavigate, Link } from 'react-router-dom';
import {
  LayoutDashboard,
  PlayCircle,
  FileText,
  Briefcase,
  History,
  BarChart3,
  Settings,
  LogOut,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/resume', label: 'Resume Analysis', icon: FileText },
    { to: '/jobs', label: 'Job Matching', icon: Briefcase },
    { to: '/setup', label: 'Mock Interview', icon: PlayCircle, highlight: true },
    { to: '/history', label: 'Reports & History', icon: History },
    { to: '/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 lg:w-72 bg-slate-950/95 border-r border-slate-800/80 flex flex-col justify-between h-screen sticky top-0 select-none overflow-y-auto">
      <div>
        {/* Brand Header - Clean Solid White Background */}
        <div className="bg-white px-5 py-5 sm:px-6 sm:py-6 border-b border-slate-200 flex items-center justify-center select-none shadow-none">
          <Link
            to="/dashboard"
            className="block transition-transform duration-200 hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-brand-500 rounded"
            title="TalentIQ Dashboard"
          >
            <img
              src="/talentiq-logo.png"
              alt="TalentIQ - Practice • Analyze • Grow"
              className="w-[136px] md:w-[152px] lg:w-[168px] h-auto object-contain block mx-auto"
              loading="eager"
            />
          </Link>
        </div>

        {/* Navigation links */}
        <nav className="p-4 space-y-1.5">
          {navLinks.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30 shadow-sm'
                      : item.highlight
                      ? 'text-brand-400 hover:bg-brand-500/10 hover:text-brand-300'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.label}</span>
                </div>
                {item.highlight && (
                  <Sparkles className="w-3.5 h-3.5 text-brand-400 animate-pulse" />
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User info & Logout */}
      <div className="p-4 border-t border-slate-800/80 space-y-3">
        {user && (
          <div className="px-3 py-2 rounded-xl bg-slate-900/60 border border-slate-800/60 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-700 to-indigo-600 flex items-center justify-center text-xs font-bold text-white uppercase">
              {user.name.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-white truncate">{user.name}</p>
              <p className="text-[10px] text-slate-400 truncate">{user.target_role || 'Candidate'}</p>
            </div>
          </div>
        )}

        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3.5 py-2 text-xs font-semibold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-xl transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
