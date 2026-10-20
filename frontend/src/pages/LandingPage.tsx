import React from 'react';
import { Link } from 'react-router-dom';
import {
  Bot,
  Sparkles,
  ArrowRight,
  Mic,
  Brain,
  FileCheck,
  TrendingUp,
  Target,
  Zap,
  ShieldCheck,
  CheckCircle2,
  ChevronRight,
  Layers,
  Award
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { ScoreRing } from '../components/common/ScoreRing';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-brand-500 selection:text-white">
      {/* Navigation */}
      <nav className="h-20 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50 px-6 sm:px-12 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 transition-transform duration-200 hover:scale-[1.01]">
          <div className="bg-white rounded-xl px-3 py-1.5 flex items-center justify-center shadow-sm border border-slate-200">
            <img src="/talentiq-logo.png" alt="TalentIQ" className="h-8 w-auto object-contain" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-white">TALENTIQ</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 bg-brand-500/20 text-brand-300 rounded border border-brand-500/30">
                AI
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium">Practice • Analyze • Grow</p>
          </div>
        </Link>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
          <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#analytics" className="hover:text-white transition-colors">Analytics</a>
          <a href="#technology" className="hover:text-white transition-colors">Technology</a>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm">Sign In</Button>
          </Link>
          <Link to="/register">
            <Button variant="primary" size="sm" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
              Start Free Interview
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 px-6 sm:px-12 max-w-7xl mx-auto text-center overflow-hidden">
        {/* Glow background accent */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-brand-500/15 blur-[120px] rounded-full pointer-events-none" />

        <div className="relative z-10 max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900 border border-brand-500/30 text-xs font-semibold text-brand-300 shadow-md">
            <Sparkles className="w-3.5 h-3.5 text-brand-400 animate-pulse" />
            <span>AI-Powered Adaptive Interview & Talent Assessment Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold text-white tracking-tight leading-[1.1]">
            Practice smarter. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 via-indigo-300 to-violet-400">
              Interview better.
            </span>
          </h1>

          <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            An AI-powered adaptive interview platform that analyzes your technical skills, verbal communication, and real-time performance with instant executive feedback.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <Link to="/register">
              <Button size="lg" variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Start Free Interview
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" leftIcon={<Bot className="w-4 h-4" />}>
                View Interactive Demo
              </Button>
            </Link>
          </div>

          <p className="text-xs text-slate-400 pt-2 flex items-center justify-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Zero credit card required • Instant mock mode available</span>
          </p>
        </div>

        {/* Hero Visual: Mock Interview Dashboard Preview */}
        <div className="mt-14 relative max-w-5xl mx-auto rounded-3xl border border-slate-800 bg-slate-900/90 shadow-2xl shadow-brand-500/10 p-4 sm:p-6 text-left overflow-hidden">
          {/* Mock Browser Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-rose-500/80" />
              <span className="w-3 h-3 rounded-full bg-amber-500/80" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
              <span className="text-xs text-slate-400 ml-2 font-mono">talentiq.app/interview/session</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="emerald" size="sm">Live Adaptive Engine</Badge>
            </div>
          </div>

          {/* Interactive Preview Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Left: AI Question Simulator */}
            <div className="md:col-span-2 p-5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Adaptive Question 2 of 5
                </span>
                <Badge variant="brand" size="sm">Technical • Hard</Badge>
              </div>
              <h3 className="text-lg font-bold text-white leading-snug">
                "In your FastAPI backend, how do you handle asynchronous operations, connection pooling, and prevent blocking the main event loop under 10k RPS throughput?"
              </h3>
              <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-1">
                  <Mic className="w-3.5 h-3.5 animate-pulse" />
                  <span>Candidate Voice Transcript (Real-Time MediaRecorder)</span>
                </div>
                <p className="italic text-slate-300">
                  "We implemented async def endpoint handlers with SQLAlchemy connection pools, offloaded CPU-heavy tasks to background workers, and added Redis caching..."
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <Badge variant="amber" size="sm">Detected Fillers: 2 ("basically", "you know")</Badge>
                <Badge variant="emerald" size="sm">Clarity: 8.8/10</Badge>
                <Badge variant="slate" size="sm">Pacing: 135 WPM (Optimal)</Badge>
              </div>
            </div>

            {/* Right: Instant Score Ring & Readiness */}
            <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col items-center justify-center text-center space-y-4">
              <ScoreRing score={86} size={110} label="Overall Score" subLabel="Strong Readiness" />
              <div className="w-full space-y-2 text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>Technical Depth</span>
                  <span className="font-bold text-white">88/100</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-brand-500 h-full w-[88%]" />
                </div>
                <div className="flex justify-between text-slate-400 pt-1">
                  <span>Communication</span>
                  <span className="font-bold text-white">82/100</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full w-[82%]" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-6 sm:px-12 border-t border-slate-900 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <Badge variant="brand" size="md">Workflow</Badge>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            How TalentIQ Works
          </h2>
          <p className="text-sm sm:text-base text-slate-400">
            From your resume and target job description to a comprehensive executive readiness report in four seamless steps.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              step: '01',
              title: 'Upload Profile & JD',
              desc: 'Upload your PDF/DOCX resume and paste the target job description to automatically extract requirements.',
              icon: FileCheck,
            },
            {
              step: '02',
              title: 'Adaptive Questioning',
              desc: 'The AI adapts in real-time—drilling deeper into weak topics or elevating difficulty when you excel.',
              icon: Brain,
            },
            {
              step: '03',
              title: 'Voice & Speech Input',
              desc: 'Answer using your microphone. Our engine transcribes speech and detects verbal fillers and pacing.',
              icon: Mic,
            },
            {
              step: '04',
              title: 'Actionable Readiness Report',
              desc: 'Receive comprehensive scores, STAR feedback, model answers, and a personalized preparation plan.',
              icon: Award,
            },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 relative space-y-3">
                <span className="text-3xl font-extrabold text-slate-800">{item.step}</span>
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Key Features Section */}
      <section id="features" className="py-20 px-6 sm:px-12 bg-slate-950/50 border-t border-slate-900 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <Badge variant="cyan" size="md">Core Capabilities</Badge>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Engineered for Serious Preparation
          </h2>
          <p className="text-sm sm:text-base text-slate-400">
            TalentIQ doesn't simply give generic interview questions. It simulates high-caliber technical and behavioral panels.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: 'Adaptive Difficulty Engine',
              desc: 'Questions evolve dynamically. If you demonstrate mastery of basics, the AI challenges you with distributed scale edge cases.',
              icon: Zap,
              badge: 'Dynamic AI',
            },
            {
              title: 'Verbal Filler & Pace Detection',
              desc: 'Analyzes spoken transcripts for phrases like "um", "like", and "basically". Computes words per minute and communication clarity.',
              icon: Mic,
              badge: 'Speech NLP',
            },
            {
              title: 'Resume & JD Gap Matcher',
              desc: 'Evaluates your candidate profile directly against target job postings, highlighting matched skills and critical missing requirements.',
              icon: Target,
              badge: 'Matching',
            },
            {
              title: 'STAR Method Evaluator',
              desc: 'Evaluates behavioral and situational responses for Situation, Task, Action, and measurable Results with model answers.',
              icon: Brain,
              badge: 'Behavioral',
            },
            {
              title: 'Progress & Trend Analytics',
              desc: 'Tracks your technical, communication, and problem-solving trajectory across multiple mock sessions with Recharts visualizer.',
              icon: TrendingUp,
              badge: 'Analytics',
            },
            {
              title: 'Zero-Cost Local Mock Mode',
              desc: 'Runs out-of-the-box with full fidelity without requiring paid API keys, with full support for OpenAI & custom providers.',
              icon: ShieldCheck,
              badge: 'Deterministic',
            },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all space-y-3">
                <div className="flex items-center justify-between">
                  <div className="p-2.5 rounded-xl bg-brand-500/10 text-brand-400">
                    <Icon className="w-5 h-5" />
                  </div>
                  <Badge variant="slate" size="sm">{item.badge}</Badge>
                </div>
                <h3 className="text-base font-bold text-white">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Technology Stack Section */}
      <section id="technology" className="py-20 px-6 sm:px-12 border-t border-slate-900 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-3">
          <Badge variant="emerald" size="md">Architecture</Badge>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Built on a Modern Full-Stack Architecture
          </h2>
          <p className="text-sm text-slate-400">
            FastAPI backend, React 18 TypeScript frontend, PostgreSQL data store, and resilient AI provider abstractions.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          {[
            { name: 'FastAPI', desc: 'Asynchronous Python Web Framework' },
            { name: 'React + Vite', desc: 'Modern TypeScript SPA' },
            { name: 'SQLAlchemy & Postgres', desc: 'Robust Relational Modeling' },
            { name: 'MediaRecorder API', desc: 'Native Browser Voice Capture' },
            { name: 'AI Provider Layer', desc: 'Mock / OpenAI / STT Whisper' },
            { name: 'Recharts', desc: 'Interactive Performance Graphs' },
            { name: 'WebSockets', desc: 'Live Room Bi-directional Events' },
            { name: 'Docker Compose', desc: 'Production-Ready Containerization' },
          ].map((tech, i) => (
            <div key={i} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <h4 className="text-sm font-bold text-white">{tech.name}</h4>
              <p className="text-[11px] text-slate-400 mt-1">{tech.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 sm:px-12 max-w-5xl mx-auto text-center">
        <div className="p-10 sm:p-16 rounded-3xl bg-gradient-to-b from-slate-900 to-slate-950 border border-brand-500/30 relative overflow-hidden space-y-6">
          <div className="absolute top-0 right-1/4 w-80 h-80 bg-brand-500/10 blur-[90px] rounded-full pointer-events-none" />

          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            Ready to ace your next technical interview?
          </h2>
          <p className="text-sm sm:text-base text-slate-300 max-w-xl mx-auto">
            Experience realistic adaptive questioning, pinpoint verbal communication habits, and elevate your interview readiness index today.
          </p>
          <div className="pt-2">
            <Link to="/register">
              <Button size="lg" variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Get Started for Free
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-10 px-6 sm:px-12 max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-brand-400" />
          <span className="font-bold text-slate-200">TALENTIQ</span>
          <span>© 2026. All rights reserved.</span>
        </div>
        <div className="flex items-center gap-6">
          <span>FastAPI</span>
          <span>•</span>
          <span>React</span>
          <span>•</span>
          <span>PostgreSQL</span>
          <span>•</span>
          <span>Docker Ready</span>
        </div>
      </footer>
    </div>
  );
};
