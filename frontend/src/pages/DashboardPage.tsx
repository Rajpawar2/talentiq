import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  PlayCircle,
  TrendingUp,
  Award,
  Target,
  Cpu,
  MessageSquare,
  ArrowRight,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Briefcase
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Skeleton } from '../components/common/FeedbackStates';
import { useAuth } from '../context/AuthContext';
import { analyticsApi } from '../api/analytics';
import type { AnalyticsOverview } from '../types';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const overview = await analyticsApi.getOverview();
        setData(overview);
      } catch (err) {
        console.error('Failed to load analytics overview', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOverview();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-2xl" />
          ))}
        </div>
        <Skeleton className="h-72 rounded-2xl" />
      </div>
    );
  }

  const statCards = [
    { label: 'Total Interviews', value: data?.total_interviews ?? 0, icon: PlayCircle, color: 'text-brand-400' },
    { label: 'Average Score', value: `${data?.average_score ?? 0}%`, icon: TrendingUp, color: 'text-indigo-400' },
    { label: 'Best Score', value: `${data?.best_score ?? 0}%`, icon: Award, color: 'text-emerald-400' },
    { label: 'Resume Match', value: `${data?.resume_match_score ?? 0}%`, icon: Target, color: 'text-amber-400' },
    { label: 'Technical Score', value: `${data?.technical_score ?? 0}%`, icon: Cpu, color: 'text-cyan-400' },
    { label: 'Communication', value: `${data?.communication_score ?? 0}%`, icon: MessageSquare, color: 'text-rose-400' },
  ];

  return (
    <div className="space-y-8">
      {/* Top Welcome Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800/80">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Welcome back, {user?.name || 'Candidate'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Track your adaptive interview progress, skill strengths, and target readiness index.
          </p>
        </div>

        <Link to="/setup">
          <Button variant="primary" size="md" rightIcon={<ArrowRight className="w-4 h-4" />}>
            Start New Interview
          </Button>
        </Link>
      </div>

      {/* 6 Key Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <Card key={i} className="p-4 bg-slate-900/70 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  {card.label}
                </span>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
              <p className="text-2xl font-black text-white tracking-tight">{card.value}</p>
            </Card>
          );
        })}
      </div>

      {/* Main Charts & Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Trend Chart (2 Cols) */}
        <Card className="lg:col-span-2 p-6 bg-slate-900/80 border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-brand-400" />
                <span>Performance Trend Over Time</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Tracking overall score trajectory across mock sessions</p>
            </div>
            <Badge variant="emerald" size="sm">+14% Growth</Badge>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.performance_trend || []}>
                <defs>
                  <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" domain={[40, 100]} fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    color: '#fff',
                    fontSize: '12px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="overall_score"
                  stroke="#818cf8"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#scoreGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Recommended Practice */}
        <Card className="p-6 bg-slate-900/80 border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-4 h-4 text-brand-400" />
              <h3 className="text-base font-bold text-white tracking-tight">Recommended Practice</h3>
            </div>
            <ul className="space-y-3">
              {data?.recommended_practice.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-xs text-slate-300 leading-relaxed p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <Link to="/setup" className="pt-4">
            <Button variant="secondary" size="sm" className="w-full">
              Simulate Recommended Scenario
            </Button>
          </Link>
        </Card>
      </div>

      {/* Skills Matrix & Recent Interviews */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skill Strengths & Gaps */}
        <Card className="p-6 bg-slate-900/80 border-slate-800 space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <Target className="w-4 h-4 text-brand-400" />
              <span>Skill Matrix & Gap Detection</span>
            </h3>
            <span className="text-xs text-slate-400">AI Assessment</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Strengths */}
            <div className="space-y-2.5">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Verified Strengths
              </span>
              {data?.skill_strengths.map((s, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <div className="flex justify-between text-xs font-medium text-slate-200 mb-1">
                    <span>{s.skill}</span>
                    <span className="text-emerald-400 font-bold">{s.level}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${s.level}%` }} />
                  </div>
                </div>
              ))}
            </div>

            {/* Gaps */}
            <div className="space-y-2.5">
              <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Focus Improvement
              </span>
              {data?.skill_gaps.map((s, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <div className="flex justify-between text-xs font-medium text-slate-200 mb-1">
                    <span>{s.skill}</span>
                    <span className="text-amber-400 font-bold">{s.level}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-amber-500 h-full rounded-full" style={{ width: `${s.level}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Recent Interviews List */}
        <Card className="p-6 bg-slate-900/80 border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-brand-400" />
              <span>Recent Interviews</span>
            </h3>
            <Link to="/history" className="text-xs text-brand-400 hover:text-brand-300 font-semibold">
              View All History →
            </Link>
          </div>

          <div className="space-y-2.5">
            {data?.recent_interviews && data.recent_interviews.length > 0 ? (
              data.recent_interviews.map((intv) => (
                <div
                  key={intv.id}
                  className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 flex items-center justify-between transition-all"
                >
                  <div className="space-y-0.5">
                    <h4 className="text-xs font-bold text-white">{intv.title}</h4>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400">
                      <Clock className="w-3 h-3" />
                      <span>{intv.created_at}</span>
                      <span>•</span>
                      <Badge variant="brand" size="sm">{intv.type}</Badge>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <span className="text-xs font-extrabold text-white block">
                        {intv.score > 0 ? `${intv.score}%` : 'In Progress'}
                      </span>
                      <span className="text-[10px] text-slate-400 capitalize">{intv.status}</span>
                    </div>

                    <Link to={intv.status === 'completed' ? `/reports/${intv.id}` : `/room/${intv.id}`}>
                      <Button size="sm" variant="outline" className="px-2.5 py-1 text-xs">
                        {intv.status === 'completed' ? 'Report' : 'Resume'}
                      </Button>
                    </Link>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-xs text-slate-400">
                No mock interviews recorded yet.{' '}
                <Link to="/setup" className="text-brand-400 font-semibold underline">
                  Launch your first one
                </Link>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
