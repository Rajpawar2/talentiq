import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Bot, Mail, Lock, ArrowRight, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register } = useAuth();
  const { addToast } = useToast();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsVerification, setNeedsVerification] = useState(false);

  useEffect(() => {
    if (location.state?.verifiedEmail) {
      setEmail(location.state.verifiedEmail);
    }
  }, [location.state]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setNeedsVerification(false);
    setIsLoading(true);

    try {
      await login(email, password);
      addToast('Welcome back to TalentIQ!', 'success');
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Invalid email or password.';
      setError(msg);
      if (msg.toLowerCase().includes('verify your email')) {
        setNeedsVerification(true);
      }
      addToast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    setError(null);
    const demoEmail = 'alex.morgan@example.com';
    const demoPass = 'DemoPass123!';

    try {
      // Attempt login first
      await login(demoEmail, demoPass);
      addToast('Signed in as Demo Candidate (Alex Morgan)', 'success');
      navigate('/dashboard');
    } catch {
      // If not yet registered in fresh DB, register automatically
      try {
        await register('Alex Morgan', demoEmail, demoPass, 'Senior AI Developer');
        addToast('Created and logged into Demo Candidate Account', 'success');
        navigate('/dashboard');
      } catch (err: any) {
        setError('Could not initialize demo account. Please try manual register.');
      }
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
          <h2 className="text-2xl font-bold text-white tracking-tight">Sign in to your account</h2>
          <p className="text-xs text-slate-400">Continue your interview preparation and progress tracking</p>
        </div>

        {/* Card */}
        <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl space-y-5">
          {/* Quick Demo Button */}
          <button
            type="button"
            onClick={handleDemoLogin}
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-xl bg-brand-500/10 hover:bg-brand-500/20 border border-brand-500/30 text-brand-300 text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-sm"
          >
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>Instant Demo Sign In (1-Click)</span>
          </button>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-slate-800 w-full" />
            <span className="bg-slate-900 px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Or with credentials
            </span>
            <div className="border-t border-slate-800 w-full" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
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
              label="Password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
            />

            {error && (
              <div className="space-y-2">
                <p className="text-xs text-rose-400 font-medium">{error}</p>
                {needsVerification && (
                  <div className="p-3 rounded-xl bg-brand-500/10 border border-brand-500/30 flex items-center justify-between text-xs">
                    <span className="text-brand-300">Email verification required</span>
                    <button
                      type="button"
                      onClick={() => navigate('/verify-email', { state: { email } })}
                      className="text-brand-400 hover:text-brand-300 font-bold underline underline-offset-2"
                    >
                      Verify Email
                    </button>
                  </div>
                )}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isLoading}
              className="w-full"
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Sign In
            </Button>
          </form>

          <p className="text-center text-xs text-slate-400 pt-2">
            Don't have an account?{' '}
            <Link to="/register" className="text-brand-400 hover:text-brand-300 font-semibold">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
