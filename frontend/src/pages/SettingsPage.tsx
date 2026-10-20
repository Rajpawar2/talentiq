import React, { useState } from 'react';
import { Settings, Cpu, Shield, Key, Volume2, CheckCircle2, Bot } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Badge } from '../components/common/Badge';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const { addToast } = useToast();

  const [aiProvider, setAiProvider] = useState<'mock' | 'openai'>('mock');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-4o-mini');
  const [targetRole, setTargetRole] = useState(user?.target_role || 'Senior Software Engineer');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    addToast('Preferences saved successfully!', 'success');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          System & Account Settings
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Manage your AI provider integration, role targeting, and simulation preferences.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Profile Card */}
        <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Bot className="w-4 h-4 text-brand-400" />
            <span>Profile Information</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Full Name
              </label>
              <input
                type="text"
                disabled
                value={user?.name || ''}
                className="w-full bg-slate-950 text-slate-300 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 opacity-80"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Email Address
              </label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full bg-slate-950 text-slate-300 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 opacity-80"
              />
            </div>
          </div>

          <div className="space-y-1.5 pt-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Target Interview Role
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
        </Card>

        {/* AI Engine & Mock Mode Card */}
        <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Cpu className="w-4 h-4 text-brand-400" />
              <span>AI Provider Configuration</span>
            </h3>
            <Badge variant="emerald" size="sm">Mock Engine Ready (Zero Cost)</Badge>
          </div>

          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start gap-3">
              <Shield className="w-5 h-5 text-brand-400 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-slate-300 leading-relaxed">
                <strong className="text-white">Deterministic Mock Mode Active: </strong>
                TalentIQ runs out-of-the-box with deterministic, high-fidelity AI questions and speech evaluations. You do not need to provide paid third-party API keys to test or evaluate candidate workflows.
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                type="button"
                onClick={() => setAiProvider('mock')}
                className={`p-3.5 rounded-xl border text-left transition-all ${
                  aiProvider === 'mock'
                    ? 'bg-brand-600/20 border-brand-500 text-white'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400'
                }`}
              >
                <span className="text-xs font-bold block">Internal Mock Provider</span>
                <span className="text-[10px] text-slate-400 mt-0.5 block">Zero latency, offline capable</span>
              </button>

              <button
                type="button"
                onClick={() => setAiProvider('openai')}
                className={`p-3.5 rounded-xl border text-left transition-all ${
                  aiProvider === 'openai'
                    ? 'bg-brand-600/20 border-brand-500 text-white'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400'
                }`}
              >
                <span className="text-xs font-bold block">External LLM (OpenAI)</span>
                <span className="text-[10px] text-slate-400 mt-0.5 block">Requires valid API Key</span>
              </button>
            </div>

            {aiProvider === 'openai' && (
              <div className="space-y-4 pt-3 animate-in fade-in duration-200">
                <Input
                  label="OpenAI API Key"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-proj-..."
                  leftIcon={<Key className="w-4 h-4" />}
                  helperText="Stored locally in session memory. Not exposed in logs."
                />

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                    Model Selection
                  </label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 px-3.5 py-2.5"
                  >
                    <option value="gpt-4o-mini">gpt-4o-mini (Fast & efficient)</option>
                    <option value="gpt-4o">gpt-4o (High precision)</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" variant="primary">
            Save Preferences
          </Button>
        </div>
      </form>
    </div>
  );
};
