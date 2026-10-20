import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Mail, CheckCircle2, ArrowRight, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import { Button } from '../components/common/Button';
import { authApi } from '../api/auth';
import { useToast } from '../context/ToastContext';

export const VerifyEmailPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { addToast } = useToast();

  // Get initial email from navigation state or URL query parameter
  const emailFromState = location.state?.email || searchParams.get('email') || '';
  const [email, setEmail] = useState<string>(emailFromState);

  // 6 separate OTP input slots
  const [otp, setOtp] = useState<string[]>(['', '', '', '', '', '']);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isResending, setIsResending] = useState<boolean>(false);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // 60-second cooldown timer
  const [cooldown, setCooldown] = useState<number>(60);

  // Focus the first empty input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  // Cooldown countdown timer
  useEffect(() => {
    if (cooldown <= 0) return;
    const interval = setInterval(() => {
      setCooldown((prev) => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [cooldown]);

  const handleOtpChange = (index: number, value: string) => {
    // Only accept numeric input
    const cleanChar = value.replace(/\D/g, '').slice(-1);
    const newOtp = [...otp];
    newOtp[index] = cleanChar;
    setOtp(newOtp);
    setError(null);

    // Auto-advance to next box if a digit was entered
    if (cleanChar && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace') {
      if (!otp[index] && index > 0) {
        // Current box is empty, jump to previous and clear it
        inputRefs.current[index - 1]?.focus();
        const newOtp = [...otp];
        newOtp[index - 1] = '';
        setOtp(newOtp);
      } else {
        const newOtp = [...otp];
        newOtp[index] = '';
        setOtp(newOtp);
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (!pastedData) return;

    const newOtp = [...otp];
    for (let i = 0; i < 6; i++) {
      newOtp[i] = pastedData[i] || '';
    }
    setOtp(newOtp);
    setError(null);

    // Focus last filled box or 6th box
    const focusIndex = Math.min(pastedData.length, 5);
    inputRefs.current[focusIndex]?.focus();
  };

  const handleVerify = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const fullOtp = otp.join('');
    if (fullOtp.length !== 6) {
      setError('Please enter the full 6-digit verification code.');
      return;
    }
    if (!email) {
      setError('Email address is missing. Please return to registration.');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      await authApi.verifyEmail(email, fullOtp);
      setIsSuccess(true);
      addToast('Email verified successfully! You can now sign in.', 'success');
      setTimeout(() => {
        navigate('/login', { state: { verifiedEmail: email } });
      }, 1600);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Invalid verification code. Please try again.';
      setError(msg);
      addToast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (cooldown > 0 || isResending || !email) return;

    setIsResending(true);
    setError(null);

    try {
      const res = await authApi.resendOtp(email);
      setCooldown(res.cooldown_seconds || 60);
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
      addToast('A new 6-digit verification code has been sent.', 'success');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Could not resend verification code. Please try again later.';
      setError(msg);
      addToast(msg, 'error');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-6 text-slate-100">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <Link to="/" className="inline-block transition-transform duration-200 hover:scale-[1.02]">
            <div className="bg-white rounded-2xl px-5 py-3 inline-flex items-center justify-center shadow-lg border border-slate-200">
              <img src="/talentiq-logo.png" alt="TalentIQ" className="w-36 h-auto object-contain" />
            </div>
          </Link>
          <h2 className="text-2xl font-bold text-white tracking-tight">Verify your email</h2>
          <p className="text-xs text-slate-400">
            We've sent a 6-digit verification code to
          </p>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/90 border border-slate-700/60 text-xs font-mono text-brand-300">
            <Mail className="w-3.5 h-3.5 text-brand-400" />
            <span>{email || 'your registered email'}</span>
          </div>
        </div>

        {/* Card */}
        <div className="p-6 sm:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-2xl space-y-6">
          {isSuccess ? (
            /* Success State Animation */
            <div className="py-8 text-center space-y-4 animate-in fade-in zoom-in-95 duration-300">
              <div className="w-16 h-16 rounded-full bg-emerald-500/20 border-2 border-emerald-500/50 flex items-center justify-center mx-auto text-emerald-400">
                <CheckCircle2 className="w-10 h-10 animate-bounce" />
              </div>
              <div className="space-y-1">
                <h3 className="text-xl font-bold text-white">Email Verified!</h3>
                <p className="text-xs text-slate-300">
                  Your TalentIQ candidate account is active. Redirecting to sign in...
                </p>
              </div>
              <Button
                variant="primary"
                size="md"
                className="w-full mt-4"
                onClick={() => navigate('/login', { state: { verifiedEmail: email } })}
              >
                Continue to Sign In
              </Button>
            </div>
          ) : (
            <form onSubmit={handleVerify} className="space-y-6">
              {/* 6-digit Segmented OTP inputs */}
              <div className="space-y-2">
                <label className="block text-center text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Enter 6-Digit Verification Code
                </label>
                <div className="flex justify-between gap-2 sm:gap-2.5">
                  {otp.map((digit, idx) => (
                    <input
                      key={idx}
                      ref={(el) => (inputRefs.current[idx] = el)}
                      type="text"
                      inputMode="numeric"
                      pattern="[0-9]*"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpChange(idx, e.target.value)}
                      onKeyDown={(e) => handleKeyDown(idx, e)}
                      onPaste={handlePaste}
                      disabled={isLoading}
                      autoComplete="one-time-code"
                      className={`w-12 h-14 sm:w-13 sm:h-16 text-center text-2xl font-mono font-bold rounded-xl border bg-slate-950/80 text-white transition-all duration-150 focus:outline-none ${
                        digit
                          ? 'border-brand-500 ring-2 ring-brand-500/30 text-brand-300 shadow-lg shadow-brand-500/10'
                          : 'border-slate-800 focus:border-brand-400 focus:ring-2 focus:ring-brand-500/20'
                      } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    />
                  ))}
                </div>
              </div>

              {/* Error message */}
              {error && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-2.5 text-xs text-rose-300 animate-in fade-in">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
                  <span className="leading-relaxed">{error}</span>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                variant="primary"
                size="md"
                isLoading={isLoading}
                disabled={otp.join('').length < 6 || isLoading}
                className="w-full py-3"
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Verify Email
              </Button>

              {/* Resend OTP Section */}
              <div className="pt-2 border-t border-slate-800/80 flex flex-col items-center gap-3">
                <div className="text-xs text-slate-400 text-center">
                  {cooldown > 0 ? (
                    <span className="text-slate-400">
                      Resend available in{' '}
                      <span className="text-brand-400 font-semibold font-mono">{cooldown} seconds</span>
                    </span>
                  ) : (
                    <button
                      type="button"
                      onClick={handleResend}
                      disabled={isResending}
                      className="inline-flex items-center gap-1.5 text-brand-400 hover:text-brand-300 font-semibold transition-colors disabled:opacity-50"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isResending ? 'animate-spin' : ''}`} />
                      <span>Resend Verification Code</span>
                    </button>
                  )}
                </div>

                {/* Change Email & Sign In Links */}
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <Link
                    to="/register"
                    className="hover:text-slate-200 transition-colors underline-offset-4 hover:underline"
                  >
                    Change Email
                  </Link>
                  <span className="text-slate-700">•</span>
                  <Link
                    to="/login"
                    className="hover:text-slate-200 transition-colors underline-offset-4 hover:underline"
                  >
                    Back to Sign In
                  </Link>
                </div>
              </div>
            </form>
          )}
        </div>

        {/* Security / Help note */}
        <p className="text-center text-[11px] text-slate-500">
          Didn't receive the email? Check your spam or promotions folder. OTPs expire in 10 minutes.
        </p>
      </div>
    </div>
  );
};
