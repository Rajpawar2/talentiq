import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  FileCheck,
  Target,
  Sparkles,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ArrowRight,
  TrendingUp,
  Layers,
  Award
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ScoreRing } from '../components/common/ScoreRing';
import { jobsApi } from '../api/jobs';
import { resumesApi } from '../api/resumes';
import type { ResumeListItem, MatchingResult, JobDescriptionData } from '../types';
import { useToast } from '../context/ToastContext';

export const JobMatchingPage: React.FC = () => {
  const { addToast } = useToast();
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('');
  const [jobTitle, setJobTitle] = useState('Senior Backend Engineer');
  const [company, setCompany] = useState('ScaleTech AI');
  const [jdText, setJdText] = useState(
    'We are hiring a Senior Backend Engineer to design high-throughput microservices. ' +
    'Required Skills: Python, FastAPI, PostgreSQL, Docker, Redis, REST APIs, System Design, CI/CD, AWS, Kubernetes.\n' +
    'Responsibilities: Design scalable asynchronous APIs, optimize database queries, build resilient pipelines.'
  );

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [matchResult, setMatchResult] = useState<MatchingResult | null>(null);

  useEffect(() => {
    const loadResumes = async () => {
      try {
        const list = await resumesApi.getResumes();
        setResumes(list);
        if (list.length > 0) {
          setSelectedResumeId(list[0].id);
        }
      } catch (err) {
        console.error('Failed to load resumes for matching', err);
      }
    };
    loadResumes();
  }, []);

  const handleAnalyzeMatch = async () => {
    if (!jdText.trim()) {
      addToast('Please enter a job description.', 'warning');
      return;
    }

    setIsAnalyzing(true);
    try {
      // Create job description first or run direct analysis
      const job = await jobsApi.createJob(jobTitle, jdText, company);
      const res = await jobsApi.analyzeMatch({
        resume_id: selectedResumeId || undefined,
        job_id: job.id,
        job_text: jdText
      });
      setMatchResult(res);
      addToast('Resume vs JD match analysis completed!', 'success');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to analyze matching.';
      addToast(msg, 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Resume & Job Description Matcher
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Perform deep semantic alignment between your candidate profile and target job posting to detect skill gaps.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Form Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-5">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-brand-400" />
              <span>Target Job Details</span>
            </h3>

            {/* Select Resume */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Candidate Resume
              </label>
              {resumes.length > 0 ? (
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.filename} ({r.skills_count} skills)
                    </option>
                  ))}
                </select>
              ) : (
                <p className="text-xs text-amber-400">
                  No resumes found. Will match using default mock candidate profile.
                </p>
              )}
            </div>

            {/* Job Title & Company */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Job Title
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="Senior Backend Engineer"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Company
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="ScaleTech AI"
                />
              </div>
            </div>

            {/* Job Description Textarea */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Job Description Text / Requirements
              </label>
              <textarea
                rows={7}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                className="w-full bg-slate-950 text-slate-100 text-xs sm:text-sm rounded-xl border border-slate-800 p-3.5 focus:outline-none focus:ring-2 focus:ring-brand-500 leading-relaxed"
                placeholder="Paste the full job posting, required qualifications, and core responsibilities here..."
              />
            </div>

            <Button
              type="button"
              onClick={handleAnalyzeMatch}
              isLoading={isAnalyzing}
              variant="primary"
              className="w-full"
              leftIcon={<Sparkles className="w-4 h-4" />}
            >
              Analyze Match & Detect Gaps
            </Button>
          </Card>
        </div>

        {/* Right Column: Match Results (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {matchResult ? (
            <div className="space-y-6 animate-in fade-in duration-300">
              {/* Score Gauge & Alignment Overview */}
              <Card className="p-6 bg-slate-900/90 border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-6">
                <div className="flex-1 space-y-2 text-center sm:text-left">
                  <Badge variant="brand" size="md">Match Breakdown</Badge>
                  <h3 className="text-xl font-bold text-white">
                    {matchResult.match_score >= 80 ? 'High Fit Candidate' : 'Moderate Alignment'}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Experience alignment is assessed as <strong className="text-emerald-400">{matchResult.experience_match}</strong>.
                    You meet {matchResult.skill_match_percentage}% of the specified technology stack.
                  </p>
                </div>

                <ScoreRing
                  score={matchResult.match_score}
                  size={130}
                  label="Match Index"
                  subLabel={`${matchResult.skill_match_percentage}% Skills`}
                />
              </Card>

              {/* Matched vs Missing Skills Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Matched Skills */}
                <Card className="p-5 bg-slate-900/90 border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      Matched Skills ({matchResult.matched_skills.length})
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {matchResult.matched_skills.length > 0 ? (
                      matchResult.matched_skills.map((s, i) => (
                        <Badge key={i} variant="emerald" size="sm">
                          ✓ {s}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">None detected</span>
                    )}
                  </div>
                </Card>

                {/* Missing Skills */}
                <Card className="p-5 bg-slate-900/90 border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                      <XCircle className="w-4 h-4 text-rose-400" />
                      Missing Skills ({matchResult.missing_skills.length})
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {matchResult.missing_skills.length > 0 ? (
                      matchResult.missing_skills.map((s, i) => (
                        <Badge key={i} variant="rose" size="sm">
                          ✗ {s}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-emerald-400">All key skills matched!</span>
                    )}
                  </div>
                </Card>
              </div>

              {/* AI Recommendations */}
              <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-brand-400" />
                  <span>Strategic Preparation Recommendations</span>
                </h3>
                <ul className="space-y-2.5">
                  {matchResult.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-xs text-slate-300 leading-relaxed p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                      <CheckCircle2 className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            </div>
          ) : (
            <Card className="p-16 text-center text-slate-400 bg-slate-900/40 border-dashed border-slate-800 space-y-3">
              <Target className="w-12 h-12 text-slate-600 mx-auto" />
              <h3 className="text-base font-bold text-white">No Match Analysis Run Yet</h3>
              <p className="text-xs max-w-sm mx-auto">
                Select your resume and enter a target job description on the left to see matched competencies and missing skills.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
