import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Award,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FileText,
  ChevronDown,
  ChevronUp,
  Cpu,
  MessageSquare,
  Target,
  Brain,
  Lightbulb,
  ArrowRight,
  RotateCcw
} from 'lucide-react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer
} from 'recharts';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ScoreRing } from '../components/common/ScoreRing';
import { Skeleton } from '../components/common/FeedbackStates';
import { interviewsApi } from '../api/interviews';
import type { InterviewReport } from '../types';
import { useToast } from '../context/ToastContext';

export const ReportPage: React.FC = () => {
  const { interviewId } = useParams<{ interviewId: string }>();
  const { addToast } = useToast();
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedQuestions, setExpandedQuestions] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!interviewId) return;
    const fetchReport = async () => {
      try {
        const data = await interviewsApi.getReport(interviewId);
        setReport(data);
        // Expand first question by default
        if (data.question_reviews && data.question_reviews.length > 0) {
          setExpandedQuestions({ [data.question_reviews[0].question_id]: true });
        }
      } catch (err) {
        addToast('Failed to load assessment report.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [interviewId]);

  const toggleExpand = (qId: string) => {
    setExpandedQuestions((prev) => ({ ...prev, [qId]: !prev[qId] }));
  };

  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto">
        <Skeleton className="h-10 w-80 rounded-xl" />
        <Skeleton className="h-64 rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-72 rounded-2xl" />
          <Skeleton className="h-72 rounded-2xl" />
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-12 text-center text-slate-400">
        <p>No report found for this interview session.</p>
        <Link to="/dashboard" className="text-brand-400 underline mt-2 block">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const radarData = [
    { category: 'Technical Depth', score: report.technical_score },
    { category: 'Communication', score: report.communication_score },
    { category: 'Problem Solving', score: report.problem_solving_score },
    { category: 'Behavioral Fit', score: report.behavioral_score },
    { category: 'Resume Fit', score: report.resume_match_score },
  ];

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="brand" size="md">Executive Evaluation</Badge>
            <Badge
              variant={
                report.interview_readiness === 'High'
                  ? 'emerald'
                  : report.interview_readiness === 'Moderate'
                  ? 'amber'
                  : 'rose'
              }
              size="md"
            >
              Readiness: {report.interview_readiness}
            </Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Interview Assessment & Readiness Report
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Comprehensive synthesis of technical mastery, verbal communication, and problem-solving structure.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/setup">
            <Button variant="primary" size="sm" rightIcon={<RotateCcw className="w-3.5 h-3.5" />}>
              Practice Again
            </Button>
          </Link>
        </div>
      </div>

      {/* Top Hero Card: Overall Score Ring + Category Breakdown */}
      <Card className="p-6 sm:p-8 bg-slate-900/90 border-slate-800">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
          {/* Score Gauge */}
          <div className="md:col-span-4 flex flex-col items-center justify-center p-4 border-b md:border-b-0 md:border-r border-slate-800">
            <ScoreRing
              score={report.overall_score}
              size={150}
              strokeWidth={12}
              label="Overall Assessment Score"
              subLabel={`${report.answered_questions} of ${report.total_questions} Questions Answered`}
            />
          </div>

          {/* Category Scores & Radar (8 cols) */}
          <div className="md:col-span-8 grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-cyan-400" /> Technical Accuracy</span>
                  <span className="text-white font-bold">{report.technical_score}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-cyan-500 h-full rounded-full" style={{ width: `${report.technical_score}%` }} />
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span className="flex items-center gap-1.5"><MessageSquare className="w-3.5 h-3.5 text-indigo-400" /> Communication Clarity</span>
                  <span className="text-white font-bold">{report.communication_score}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${report.communication_score}%` }} />
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span className="flex items-center gap-1.5"><Brain className="w-3.5 h-3.5 text-emerald-400" /> Problem Solving</span>
                  <span className="text-white font-bold">{report.problem_solving_score}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${report.problem_solving_score}%` }} />
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
                  <span className="flex items-center gap-1.5"><Target className="w-3.5 h-3.5 text-amber-400" /> Behavioral / STAR</span>
                  <span className="text-white font-bold">{report.behavioral_score}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full" style={{ width: `${report.behavioral_score}%` }} />
                </div>
              </div>
            </div>

            {/* Radar Visualizer */}
            <div className="h-56 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="category" stroke="#94a3b8" fontSize={9} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={8} />
                  <Radar name="Score" dataKey="score" stroke="#818cf8" fill="#6366f1" fillOpacity={0.4} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="mt-6 pt-6 border-t border-slate-800">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Executive Summary
          </h3>
          <p className="text-sm text-slate-200 leading-relaxed bg-slate-950/50 p-4 rounded-xl border border-slate-800/80">
            {report.detailed_summary}
          </p>
        </div>
      </Card>

      {/* Strengths & Weaknesses Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths */}
        <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Demonstrated Strengths</span>
          </h3>
          <ul className="space-y-2.5">
            {report.key_strengths.map((str, i) => (
              <li key={i} className="flex items-start gap-2.5 text-xs text-slate-300 leading-relaxed p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </Card>

        {/* Weak Areas */}
        <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Opportunities for Growth</span>
          </h3>
          <ul className="space-y-2.5">
            {report.weak_areas.map((weak, i) => (
              <li key={i} className="flex items-start gap-2.5 text-xs text-slate-300 leading-relaxed p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <span>{weak}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* Personalized Action Plan */}
      <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
        <h3 className="text-xs font-bold text-brand-300 uppercase tracking-wider flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-brand-400" />
          <span>Personalized Preparation Plan</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {report.prep_plan.map((step, i) => (
            <div key={i} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <span className="text-xs font-extrabold text-brand-400">Step {i + 1}</span>
              <p className="text-xs text-slate-300 leading-relaxed">{step}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Question by Question Review */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
          <FileText className="w-5 h-5 text-brand-400" />
          <span>Question-by-Question Detailed Review</span>
        </h2>

        <div className="space-y-3">
          {report.question_reviews.map((rev) => {
            const isExpanded = !!expandedQuestions[rev.question_id];
            const evalObj = rev.evaluation;

            return (
              <div
                key={rev.question_id}
                className="rounded-2xl border border-slate-800 bg-slate-900/70 overflow-hidden transition-all"
              >
                {/* Question Row Header */}
                <div
                  onClick={() => toggleExpand(rev.question_id)}
                  className="p-4 sm:p-5 flex items-center justify-between cursor-pointer hover:bg-slate-850/60 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-7 h-7 rounded-lg bg-slate-800 text-xs font-extrabold text-white flex items-center justify-center">
                      Q{rev.question_index}
                    </span>
                    <div>
                      <h4 className="text-sm font-bold text-white leading-tight">
                        {rev.question_text}
                      </h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="brand" size="sm">{rev.category}</Badge>
                        <Badge variant="slate" size="sm">{rev.difficulty_level}</Badge>
                        {rev.is_follow_up && (
                          <Badge variant="emerald" size="sm">Adaptive Follow-Up</Badge>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {evalObj && (
                      <span className="text-xs font-black text-brand-300 px-2.5 py-1 rounded-lg bg-brand-500/10 border border-brand-500/20">
                        {Math.round(evalObj.overall_score * 10)}/100
                      </span>
                    )}
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Expandable Content Body */}
                {isExpanded && (
                  <div className="p-5 pt-0 border-t border-slate-800/80 space-y-4 text-xs mt-3">
                    {/* Candidate Answer */}
                    <div className="space-y-1.5">
                      <span className="font-bold text-slate-400 uppercase tracking-wider block text-[10px]">
                        Your Answer ({rev.input_mode === 'voice' ? 'Spoken Voice' : 'Text'})
                      </span>
                      <p className="p-3.5 rounded-xl bg-slate-950 text-slate-200 leading-relaxed border border-slate-800 italic">
                        "{rev.candidate_answer || 'No answer submitted.'}"
                      </p>
                      {rev.filler_count !== undefined && rev.filler_count > 0 && (
                        <p className="text-[11px] text-amber-400 pt-0.5">
                          Detected verbal fillers: {rev.filler_count} word(s)
                        </p>
                      )}
                    </div>

                    {/* AI Constructive Feedback */}
                    {evalObj && evalObj.feedback && (
                      <div className="space-y-1.5">
                        <span className="font-bold text-indigo-400 uppercase tracking-wider block text-[10px]">
                          AI Evaluation & Feedback
                        </span>
                        <p className="p-3.5 rounded-xl bg-indigo-950/20 text-indigo-200 leading-relaxed border border-indigo-500/30">
                          {evalObj.feedback}
                        </p>
                      </div>
                    )}

                    {/* Ideal STAR / Technical Answer */}
                    {evalObj && evalObj.ideal_answer && (
                      <div className="space-y-1.5">
                        <span className="font-bold text-emerald-400 uppercase tracking-wider block text-[10px]">
                          Model Benchmark Answer
                        </span>
                        <p className="p-3.5 rounded-xl bg-emerald-950/20 text-emerald-200 leading-relaxed border border-emerald-500/30">
                          {evalObj.ideal_answer}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
