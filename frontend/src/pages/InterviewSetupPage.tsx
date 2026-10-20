import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Bot,
  Briefcase,
  Layers,
  Clock,
  HelpCircle,
  Building,
  FileText,
  Sliders,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { interviewsApi } from '../api/interviews';
import { resumesApi } from '../api/resumes';
import { jobsApi } from '../api/jobs';
import type { ResumeListItem, JobDescriptionData } from '../types';
import { useToast } from '../context/ToastContext';

export const InterviewSetupPage: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [role, setRole] = useState('Senior Full-Stack AI Engineer');
  const [interviewType, setInterviewType] = useState('Technical');
  const [difficulty, setDifficulty] = useState('Medium');
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [durationMinutes, setDurationMinutes] = useState(30);
  const [company, setCompany] = useState('Anthropic Labs');
  const [sourceOption, setSourceOption] = useState<'both' | 'resume' | 'job'>('both');

  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [jobs, setJobs] = useState<JobDescriptionData[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('');
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    const loadContextData = async () => {
      try {
        const [rList, jList] = await Promise.all([
          resumesApi.getResumes(),
          jobsApi.getJobs(),
        ]);
        setResumes(rList);
        setJobs(jList);
        if (rList.length > 0) setSelectedResumeId(rList[0].id);
        if (jList.length > 0) setSelectedJobId(jList[0].id);
      } catch (err) {
        console.error('Failed to load setup context', err);
      }
    };
    loadContextData();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    try {
      const interview = await interviewsApi.createInterview({
        role,
        interview_type: interviewType,
        difficulty,
        total_questions: totalQuestions,
        duration_minutes: durationMinutes,
        company: company.trim() || undefined,
        resume_id: sourceOption !== 'job' ? (selectedResumeId || undefined) : undefined,
        job_id: sourceOption !== 'resume' ? (selectedJobId || undefined) : undefined,
      });

      addToast('Adaptive interview session created! Starting room...', 'success');
      navigate(`/room/${interview.id}`);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to generate interview questions.';
      addToast(msg, 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-xs font-semibold text-brand-300 mb-2">
          <Sparkles className="w-3.5 h-3.5 text-brand-400" />
          <span>Adaptive Interview Configuration</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Configure Your Mock Interview
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Customize target role, difficulty, duration, and data sources. The AI synthesizes personalized, non-generic questions.
        </p>
      </div>

      <form onSubmit={handleGenerate} className="space-y-6">
        <Card className="p-6 sm:p-8 bg-slate-900/90 border-slate-800 space-y-6">
          {/* Target Role & Company */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Target Job Role *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Briefcase className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 pl-10 pr-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="e.g. AI Developer"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Target Company (Optional)
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Building className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 pl-10 pr-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="e.g. Google, Stripe, Vercel"
                />
              </div>
            </div>
          </div>

          {/* Interview Type Selector */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Interview Type
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { type: 'Technical', desc: 'System design, APIs & algorithms' },
                { type: 'Behavioral', desc: 'STAR leadership & teamwork' },
                { type: 'Mixed', desc: 'Balanced tech & culture fit' },
                { type: 'Coding', desc: 'Architectural problem-solving' },
              ].map((item) => (
                <button
                  type="button"
                  key={item.type}
                  onClick={() => setInterviewType(item.type)}
                  className={`p-3.5 rounded-xl border text-left transition-all ${
                    interviewType === item.type
                      ? 'bg-brand-600/20 border-brand-500 text-white shadow-md'
                      : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <span className="text-xs font-bold block">{item.type}</span>
                  <span className="text-[10px] text-slate-400 mt-0.5 block leading-tight">{item.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty & Length Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Difficulty */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Difficulty
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="Easy">Easy (Foundations)</option>
                <option value="Medium">Medium (Industry Standard)</option>
                <option value="Hard">Hard (Staff / Principal Level)</option>
              </select>
            </div>

            {/* Questions count */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Questions
              </label>
              <select
                value={totalQuestions}
                onChange={(e) => setTotalQuestions(Number(e.target.value))}
                className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value={5}>5 Questions (Express Mock)</option>
                <option value={10}>10 Questions (Standard)</option>
                <option value={15}>15 Questions (Comprehensive)</option>
                <option value={20}>20 Questions (Deep Dive)</option>
              </select>
            </div>

            {/* Duration */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Duration
              </label>
              <select
                value={durationMinutes}
                onChange={(e) => setDurationMinutes(Number(e.target.value))}
                className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value={15}>15 Minutes</option>
                <option value={30}>30 Minutes</option>
                <option value={45}>45 Minutes</option>
                <option value={60}>60 Minutes</option>
              </select>
            </div>
          </div>

          {/* Context Sources */}
          <div className="space-y-3 pt-2 border-t border-slate-800">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Personalization Context Source
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'both', label: 'Resume & Job Description', desc: 'Highest personalization' },
                { id: 'resume', label: 'Resume Only', desc: 'Tailored to past projects' },
                { id: 'job', label: 'Job Description Only', desc: 'Tailored to role requirements' },
              ].map((s) => (
                <button
                  type="button"
                  key={s.id}
                  onClick={() => setSourceOption(s.id as any)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    sourceOption === s.id
                      ? 'bg-brand-600/20 border-brand-500 text-white shadow-sm'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <span className="text-xs font-bold block">{s.label}</span>
                  <span className="text-[10px] text-slate-400 mt-0.5 block">{s.desc}</span>
                </button>
              ))}
            </div>

            {/* Resume Selector if applicable */}
            {sourceOption !== 'job' && resumes.length > 0 && (
              <div className="pt-2">
                <span className="text-xs text-slate-400 block mb-1">Select Resume:</span>
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 text-xs rounded-xl border border-slate-800 px-3 py-2"
                >
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.filename} ({r.skills_count} skills)
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="pt-4">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isGenerating}
              className="w-full"
              leftIcon={<Sparkles className="w-5 h-5 text-brand-300" />}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Generate Interview & Enter Room
            </Button>
          </div>
        </Card>
      </form>
    </div>
  );
};
