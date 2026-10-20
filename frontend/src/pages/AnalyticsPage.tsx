import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  BarChart2,
  Brain,
  CheckCircle2,
  Sparkles,
  Target,
  Cpu,
  MessageSquare
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Skeleton } from '../components/common/FeedbackStates';
import { analyticsApi } from '../api/analytics';
import type { AnalyticsProgress } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsProgress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const res = await analyticsApi.getProgress();
        setData(res);
      } catch (err) {
        console.error('Failed to load progress analytics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProgress();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto">
        <Skeleton className="h-10 w-64 rounded-xl" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 rounded-2xl" />
          <Skeleton className="h-80 rounded-2xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Performance Analytics & Growth Trajectory
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Deep-dive into your multi-dimensional progress across technical mastery, verbal clarity, and problem solving.
        </p>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Score Over Time Line Chart (7 Cols) */}
        <Card className="lg:col-span-7 p-6 bg-slate-900/90 border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-brand-400" />
                <span>Multi-Category Growth Curve</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Tracking score progression across mock interviews</p>
            </div>
            <Badge variant="emerald" size="sm">Upward Momentum</Badge>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data?.score_over_time || []}>
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
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line
                  type="monotone"
                  dataKey="overall_score"
                  name="Overall Index"
                  stroke="#818cf8"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="technical_score"
                  name="Technical Depth"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                />
                <Line
                  type="monotone"
                  dataKey="communication_score"
                  name="Communication"
                  stroke="#34d399"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Skill Competency Radar (5 Cols) */}
        <Card className="lg:col-span-5 p-6 bg-slate-900/90 border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Brain className="w-4 h-4 text-indigo-400" />
                <span>Competency Radar</span>
              </h3>
              <Badge variant="brand" size="sm">Current vs Industry</Badge>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">Benchmarked against senior engineering candidate standards</p>
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={data?.skill_radar || []}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={9} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={8} />
                <Radar name="Candidate" dataKey="score" stroke="#818cf8" fill="#6366f1" fillOpacity={0.4} />
                <Radar name="Benchmark" dataKey="benchmark" stroke="#64748b" fill="#64748b" fillOpacity={0.1} />
                <Legend wrapperStyle={{ fontSize: '10px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* AI Improvement Insights */}
      <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-brand-300 uppercase tracking-wider flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-brand-400" />
          <span>Automated Improvement Insights</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data?.improvement_insights.map((insight, i) => (
            <div key={i} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <p className="text-xs text-slate-200 leading-relaxed">{insight}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
