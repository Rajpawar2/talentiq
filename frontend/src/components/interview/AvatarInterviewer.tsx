import React from 'react';
import { Bot, Volume2, Sparkles } from 'lucide-react';

interface AvatarInterviewerProps {
  status: 'idle' | 'speaking' | 'listening' | 'evaluating';
  interviewerName?: string;
  role?: string;
}

export const AvatarInterviewer: React.FC<AvatarInterviewerProps> = ({
  status,
  interviewerName = 'TalentIQ AI Interlocutor',
  role = 'Staff Technical Interviewer',
}) => {
  const getStatusText = () => {
    switch (status) {
      case 'speaking':
        return 'Asking question...';
      case 'listening':
        return 'Listening to your response...';
      case 'evaluating':
        return 'Analyzing answer & adapting...';
      default:
        return 'Ready for your answer';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'speaking':
        return 'bg-brand-500/20 text-brand-300 border-brand-500/30';
      case 'listening':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'evaluating':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80">
      {/* Avatar Circle with Audio Waves */}
      <div className="relative mb-4">
        {/* Animated aura rings */}
        {status === 'speaking' && (
          <div className="absolute inset-0 rounded-full bg-brand-500/20 animate-ping scale-125" />
        )}
        {status === 'listening' && (
          <div className="absolute inset-0 rounded-full bg-emerald-500/20 animate-ping scale-110" />
        )}
        {status === 'evaluating' && (
          <div className="absolute inset-0 rounded-full bg-amber-500/20 animate-pulse scale-115" />
        )}

        <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-brand-700 via-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-2xl relative z-10 border-2 border-brand-400/30">
          <Bot className="w-12 h-12 text-white" />
          
          {/* Subtle audio waves indicator */}
          {status === 'speaking' && (
            <div className="absolute -bottom-2 px-2 py-0.5 rounded-full bg-brand-600 text-[10px] font-bold flex items-center gap-1 shadow-md">
              <Volume2 className="w-3 h-3 animate-bounce" />
              <span>Speaking</span>
            </div>
          )}
        </div>
      </div>

      {/* Interlocutor info */}
      <h3 className="text-base font-bold text-white tracking-tight">{interviewerName}</h3>
      <p className="text-xs text-slate-400 mb-3">{role}</p>

      {/* Dynamic Status Badge */}
      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor()} transition-all duration-300`}>
        {status === 'evaluating' ? (
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <span className={`w-2 h-2 rounded-full ${
            status === 'speaking' ? 'bg-brand-400 animate-pulse' :
            status === 'listening' ? 'bg-emerald-400 animate-pulse' :
            status === 'evaluating' ? 'bg-amber-400' : 'bg-slate-400'
          }`} />
        )}
        <span>{getStatusText()}</span>
      </div>

      {/* Equalizer animation for speaking / listening */}
      {(status === 'speaking' || status === 'listening') && (
        <div className="flex items-center gap-1 mt-4 h-6">
          <span className="w-1 bg-brand-400 rounded-full h-3 animate-[pulse_0.6s_ease-in-out_infinite]" />
          <span className="w-1 bg-brand-400 rounded-full h-6 animate-[pulse_0.8s_ease-in-out_infinite_0.2s]" />
          <span className="w-1 bg-brand-400 rounded-full h-4 animate-[pulse_0.7s_ease-in-out_infinite_0.4s]" />
          <span className="w-1 bg-brand-400 rounded-full h-5 animate-[pulse_0.9s_ease-in-out_infinite_0.1s]" />
          <span className="w-1 bg-brand-400 rounded-full h-2 animate-[pulse_0.5s_ease-in-out_infinite_0.3s]" />
        </div>
      )}
    </div>
  );
};
