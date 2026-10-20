import React from 'react';
import { Badge } from '../common/Badge';
import { Sparkles, MessageSquare, Activity, CheckCircle2 } from 'lucide-react';
import type { AnswerResponse } from '../../types';

interface SpeechFeedbackProps {
  lastAnswer: AnswerResponse | null;
}

export const SpeechFeedback: React.FC<SpeechFeedbackProps> = ({ lastAnswer }) => {
  if (!lastAnswer) return null;

  const {
    filler_words_count,
    filler_breakdown,
    filler_frequency_pct,
    words_count,
    speech_pace_wpm,
    communication_indicators,
  } = lastAnswer;

  return (
    <div className="p-4 sm:p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-3.5 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-brand-400" />
          Speech & Communication Indicators
        </h4>
        <span className="text-[11px] text-slate-400">
          Last Answer ({words_count} words)
        </span>
      </div>

      {/* Metric badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block font-medium">Filler Count</span>
          <span className={`text-sm font-bold ${filler_words_count > 3 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {filler_words_count} {filler_words_count === 1 ? 'word' : 'words'}
          </span>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block font-medium">Filler Frequency</span>
          <span className={`text-sm font-bold ${filler_frequency_pct > 5 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {filler_frequency_pct}%
          </span>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block font-medium">Clarity Indicator</span>
          <span className="text-sm font-bold text-brand-300">
            {communication_indicators?.clarity_indicator || 8.5}/10
          </span>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block font-medium">Estimated Pace</span>
          <span className="text-sm font-bold text-white">
            {Math.round(speech_pace_wpm || 130)} WPM
          </span>
        </div>
      </div>

      {/* Specific fillers detected pills */}
      {filler_breakdown && Object.keys(filler_breakdown).length > 0 && (
        <div className="pt-1 flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] text-slate-400 mr-1">Detected Fillers:</span>
          {Object.entries(filler_breakdown).map(([word, count]) => (
            <Badge key={word} variant="amber" size="sm">
              "{word}": {count}x
            </Badge>
          ))}
        </div>
      )}

      {/* Observation feedback */}
      {communication_indicators?.observations && (
        <p className="text-xs text-slate-300/90 leading-relaxed italic bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/50">
          "{communication_indicators.observations}"
        </p>
      )}
    </div>
  );
};
