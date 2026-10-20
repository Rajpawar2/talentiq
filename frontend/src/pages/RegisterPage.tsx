import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bot, User as UserIcon, Mail, Lock, Briefcase, ArrowRight } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { addToast } = useToast();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [targetRole, setTargetRole] = useState('Full-Stack Engineer');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const res = await register(name, email, password, targetRole);
      addToast('Verification email sent successfully.', 'success');
      navigate('/verify-email', { state: { email: res.email || email.trim().toLowerCase() } });
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Registration failed. Please check your information.';
      setError(msg);
      addToast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-6 text-slate-100">
      <div className="w-full max-w-md space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <Link to="/" className="inline-block transition-transform duration-200 hover:scale-[1.02]">
            <div className="bg-white rounded-2xl px-5 py-3 inline-flex items-center justify-center shadow-lg border border-slate-200">
              <img src="/talentiq-logo.png" alt="TalentIQ" className="w-36 h-auto object-contain" />
            </div>
          </Link>
          <h2 className="text-2xl font-bold text-white tracking-tight">Create your account</h2>
          <p className="text-xs text-slate-400">Start simulating real interviews with adaptive feedback</p>
        </div>

        {/* Card */}
        <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl space-y-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Alex Morgan"
              leftIcon={<UserIcon className="w-4 h-4" />}
            />

            <Input
              label="Email Address"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@example.com"
              leftIcon={<Mail className="w-4 h-4" />}
            />

            <Input
              label="Password (min. 6 chars)"
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
            />

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Target Job Role
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Briefcase className="w-4 h-4" />
                </div>
                <select
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full bg-slate-900/90 text-slate-100 text-sm rounded-xl border border-slate-800 pl-10 pr-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 hover:border-slate-700"
                >
                  <option value="Full-Stack Engineer">Full-Stack Engineer</option>
                  <option value="Senior AI / ML Engineer">Senior AI / ML Engineer</option>
                  <option value="Backend Developer (Python/FastAPI)">Backend Developer (Python/FastAPI)</option>
                  <option value="Frontend Engineer (React/TypeScript)">Frontend Engineer (React/TypeScript)</option>
                  <option value="Staff Systems Architect">Staff Systems Architect</option>
                  <option value="Engineering Manager">Engineering Manager</option>
                </select>
              </div>
            </div>

            {error && <p className="text-xs text-rose-400 font-medium">{error}</p>}

            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isLoading}
              className="w-full"
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Create Account
            </Button>
          </form>

          <p className="text-center text-xs text-slate-400 pt-2">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-400 hover:text-brand-300 font-semibold">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
