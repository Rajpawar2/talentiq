import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { History, Clock, Award, ArrowRight, PlayCircle, FileText, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Skeleton } from '../components/common/FeedbackStates';
import { interviewsApi } from '../api/interviews';
import type { InterviewSession } from '../types';

export const HistoryPage: React.FC = () => {
  const [interviews, setInterviews] = useState<InterviewSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const list = await interviewsApi.getInterviews();
        setInterviews(list);
      } catch (err) {
        console.error('Failed to load history', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4 max-w-5xl mx-auto">
        <Skeleton className="h-10 w-64 rounded-xl" />
        <Skeleton className="h-64 rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Interview History
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Review past mock simulations, track score progressions, and re-examine executive feedback.
          </p>
        </div>

        <Link to="/setup">
          <Button variant="primary" size="sm" rightIcon={<ArrowRight className="w-4 h-4" />}>
            New Interview
          </Button>
        </Link>
      </div>

      {interviews.length > 0 ? (
        <Card className="p-0 bg-slate-900/80 border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Role & Session</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Difficulty</th>
                  <th className="px-6 py-4">Score</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {interviews.map((intv) => (
                  <tr key={intv.id} className="hover:bg-slate-850/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-white text-sm">{intv.role}</div>
                      <div className="text-slate-400 text-[11px]">{intv.company || 'Standard Tech Panel'}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="brand" size="sm">{intv.interview_type}</Badge>
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      {intv.difficulty}
                    </td>
                    <td className="px-6 py-4 font-bold">
                      {intv.overall_score && intv.overall_score > 0 ? (
                        <span className="text-emerald-400">{intv.overall_score}%</span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <Badge
                        variant={intv.status === 'completed' ? 'emerald' : 'amber'}
                        size="sm"
                      >
                        {intv.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-[11px]">
                      {new Date(intv.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {intv.status === 'completed' ? (
                        <Link to={`/reports/${intv.id}`}>
                          <Button size="sm" variant="outline" className="text-xs">
                            View Report
                          </Button>
                        </Link>
                      ) : (
                        <Link to={`/room/${intv.id}`}>
                          <Button size="sm" variant="primary" className="text-xs">
                            Resume Room
                          </Button>
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card className="p-16 text-center text-slate-400 bg-slate-900/40 border-dashed border-slate-800 space-y-3">
          <History className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Interviews Completed Yet</h3>
          <p className="text-xs max-w-sm mx-auto">
            Ready to test your readiness? Launch your first adaptive interview session in seconds.
          </p>
          <div className="pt-2">
            <Link to="/setup">
              <Button variant="primary" size="md">
                Start Interview Session
              </Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
};
